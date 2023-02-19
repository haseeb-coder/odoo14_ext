# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date, datetime, time, timedelta
# from pkg_resources import _
from pytz import timezone
from xlsxwriter import workbook

from src.odoo.odoo.exceptions import ValidationError
from odoo.tools.misc import xlwt
import io
import xlwt
from xlsxwriter.workbook import Workbook

import base64


class EmployeeExtWizard(models.TransientModel):
    _name = 'employee.ext.wizard'
    _description = "Wizard: Quick Report generator"

    employee_ids = fields.Many2many('hr.employee', string='Employee Name')
    department_ids = fields.Many2many('hr.department', 'employee_department_rel', 'dept_id', 'emp_id',
                                      string='Department Name')
    date_from = fields.Date(string='Start Date')
    date_to = fields.Date(string='End Date')
    customer_check = fields.Boolean(default=False, tracking=True, )
    customer_ids = fields.Many2many('res.partner', string='Customer')

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        if self.filtered(lambda c: c.date_to and c.date_from > c.date_to):
            raise ValidationError(_("start date must be earlier than  end date."))

    def pdfreport(self):
        cus_domain = []
        domain = []
        datas = []
        customer_datas = []
        leads = 0
        invoice = 0
        purchase = 0
        s_credit = 0
        p_credit = 0
        p_invoice = 0
        sale_order = 0
        pu_order = 0
        expenses = 0.0
        customer_res = {}
        start_date = self.date_from
        end_date = self.date_to
        delta = end_date - start_date
        if self.customer_check:
            customer_check = True
            if self.customer_ids:
                cus = self.env['res.partner'].search([('id', 'in', self.customer_ids.ids)])
                for ids in cus:
                    cus_domain.append(ids)
            customers = self.env['res.partner'].search([('id', 'in', [id.id for id in cus_domain])])
            for customer in customers:
                for i in range(delta.days):
                    customer_days = start_date + timedelta(days=i)
                    sale_invoice = self.env['account.move'].search(
                        [('partner_id', '=', customer.id), ('invoice_date', '=', customer_days),
                         ('move_type', '=', 'out_invoice')]).amount_total
                    purchase_invoice = self.env['account.move'].search(
                        [('partner_id', '=', customer.id), ('invoice_date', '=', customer_days),
                         ('move_type', '=', 'in_invoice')]).amount_total
                    sale_credit = self.env['account.move'].search(
                        [('partner_id', '=', customer.id), ('invoice_date', '=', customer_days),
                         ('move_type', '=', 'out_refund')]).amount_total
                    purchase_credit = self.env['account.move'].search(
                        [('partner_id', '=', customer.id), ('invoice_date', '=', customer_days),
                         ('move_type', '=', 'in_refund')]).amount_total
                    customer_lead = len(self.env['crm.lead'].search([('partner_id', '=', customer.id)]))

                    customer_sale = self.env['sale.order'].search(
                        [('partner_id', '=', customer.id), ('date_order', '>=', str(customer_days) + ' 00:00:00'),
                         ('date_order', '<=', str(customer_days) + ' 23:59:59')])
                    for sale in customer_sale:
                        order = sale.amount_total
                        sale_order = sale_order + order

                    purchase_order = self.env['purchase.order'].search(
                        [('partner_id', '=', customer.id), ('date_approve', '>=', str(customer_days) + ' 00:00:00'),
                         ('date_approve', '<=', str(customer_days) + ' 23:59:59')])
                    for purchase in purchase_order:
                        pur = purchase.amount_total
                        pu_order = pu_order + pur

                    if customer_lead:
                        leads = customer_lead

                    if customer_sale:
                        sale_order = sale_order

                    if purchase_order:
                        purchase = pu_order
                    if sale_invoice:
                        invoice += sale_invoice
                    if purchase_invoice:
                        p_invoice += purchase_invoice
                    if sale_credit:
                        s_credit += sale_credit
                    if purchase_credit:
                        p_credit += purchase_credit
                customer_datas.append({
                    'id': customer.id,
                    'name': customer.name,
                    'leads': leads,
                    'sale_order': sale_order,
                    'purchase': purchase,
                    'invoice': invoice,
                    'p_invoice': p_invoice,
                    's_credit': s_credit,
                    'p_credit': p_credit

                })

            customer_res = {
                "customers": customer_datas
            }
        else:
            if self.employee_ids:
                emp = self.env['hr.employee'].search([('id', 'in', self.employee_ids.ids)])
                for ids in emp:
                    domain.append(ids)
            if self.department_ids:
                departments = self.env['hr.employee'].search([('department_id', 'in', self.department_ids.ids)])
                for ids in departments:
                    domain.append(ids)
        employees = self.env['hr.employee'].search([('id', 'in', [id.id for id in domain])])
        for employee in employees:
            present = 0
            absent = 0
            leave = 0
            expense = 0.0
            tz = timezone(employee.resource_calendar_id.tz)
            date_from = tz.localize(datetime.combine(fields.Datetime.from_string(str(self.date_from)), time.min))
            date_to = tz.localize(datetime.combine(fields.Datetime.from_string(str(self.date_to)), time.max))
            # delta = end_date - start_date
            for i in range(delta.days):
                day = start_date + timedelta(days=i)
                expenses = self.env['hr.expense'].search(
                    [('employee_id', '=', employee.id), ('date', '=', day)]).total_amount
            intervals = employee.list_work_time_per_day(date_from, date_to, calendar=employee.resource_calendar_id)
            for rec in intervals:
                attendances = self.env['hr.attendance'].search(
                    [('employee_id', '=', employee.id), ('check_in', '>=', rec[0]), ('check_in', '<=', rec[0])])

                new_date = (rec[0])
                leaves = self.env['hr.leave'].search(
                    [('employee_id', '=', employee.id), '|',
                     ('request_date_from', '=', new_date),
                     ('request_date_from', '=', new_date)])

                if attendances:
                    present += 1
                else:
                    absent += 1
                if leaves:
                    leave += 1
                if expenses:
                    expense += expenses
            datas.append({
                'id': employee.id,
                'name': employee.name,
                'present': present,
                'absent': absent,
                'leave': leave,
                'expense': expense,
                'department': employee.department_id.name
            })
        res = {
            'attendances': datas,
        }
        data = {
            'employee_id': self.employee_ids.ids,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'form': res,
            'customer_form': customer_res,
            'customer_check': self.customer_check,

        }
        return self.env.ref('employee_ext.employee_ext_pdf_report').report_action(self, data=data)

    def excelreport(self):
        domain = []
        cus_domain = []
        datas = []
        customer_datas = []
        leads = 0
        invoice = 0
        purchase = 0
        s_credit = 0
        p_credit = 0
        p_invoice = 0
        sale_order = 0
        pu_order = 0
        customer_res = {}
        expenses = 0.0
        start_date = self.date_from
        end_date = self.date_to
        delta = end_date - start_date
        if self.customer_check:
            customer_check = True
            if self.customer_ids:
                cus = self.env['res.partner'].search([('id', 'in', self.customer_ids.ids)])
                for ids in cus:
                    cus_domain.append(ids)
            customers = self.env['res.partner'].search([('id', 'in', [id.id for id in cus_domain])])
            for customer in customers:
                for i in range(delta.days):
                    customer_days = start_date + timedelta(days=i)
                    sale_invoice = self.env['account.move'].search(
                        [('partner_id', '=', customer.id), ('invoice_date', '=', customer_days),
                         ('move_type', '=', 'out_invoice')]).amount_total
                    purchase_invoice = self.env['account.move'].search(
                        [('partner_id', '=', customer.id), ('invoice_date', '=', customer_days),
                         ('move_type', '=', 'in_invoice')]).amount_total
                    sale_credit = self.env['account.move'].search(
                        [('partner_id', '=', customer.id), ('invoice_date', '=', customer_days),
                         ('move_type', '=', 'out_refund')]).amount_total
                    purchase_credit = self.env['account.move'].search(
                        [('partner_id', '=', customer.id), ('invoice_date', '=', customer_days),
                         ('move_type', '=', 'in_refund')]).amount_total
                    customer_lead = len(self.env['crm.lead'].search([('partner_id', '=', customer.id)]))

                    customer_sale = self.env['sale.order'].search(
                        [('partner_id', '=', customer.id), ('date_order', '>=', str(customer_days) + ' 00:00:00'),
                         ('date_order', '<=', str(customer_days) + ' 23:59:59')])
                    for sale in customer_sale:
                        order = sale.amount_total
                        sale_order = sale_order + order

                    purchase_order = self.env['purchase.order'].search(
                        [('partner_id', '=', customer.id), ('date_approve', '>=', str(customer_days) + ' 00:00:00'),
                         ('date_approve', '<=', str(customer_days) + ' 23:59:59')])
                    for purchase in purchase_order:
                        pur = purchase.amount_total
                        pu_order = pu_order + pur

                    if customer_lead:
                        leads = customer_lead

                    if customer_sale:
                        sale_order = sale_order

                    if purchase_order:
                        purchase = pu_order
                    if sale_invoice:
                        invoice += sale_invoice
                    if purchase_invoice:
                        p_invoice += purchase_invoice
                    if sale_credit:
                        s_credit += sale_credit
                    if purchase_credit:
                        p_credit += purchase_credit
                customer_datas.append({
                    'id': customer.id,
                    'name': customer.name,
                    'leads': leads,
                    'sale_order': sale_order,
                    'purchase': purchase,
                    'invoice': invoice,
                    'p_invoice': p_invoice,
                    's_credit': s_credit,
                    'p_credit': p_credit

                })

        else:
            if self.employee_ids:
                emp = self.env['hr.employee'].search([('id', 'in', self.employee_ids.ids)])
                for ids in emp:
                    domain.append(ids)
            if self.department_ids:
                departments = self.env['hr.employee'].search([('department_id', 'in', self.department_ids.ids)])
                for ids in departments:
                    domain.append(ids)
        employees = self.env['hr.employee'].search([('id', 'in', [id.id for id in domain])])
        for employee in employees:
            present = 0
            absent = 0
            leave = 0
            expense = 0.0
            tz = timezone(employee.resource_calendar_id.tz)
            date_from = tz.localize(datetime.combine(fields.Datetime.from_string(str(self.date_from)), time.min))
            date_to = tz.localize(datetime.combine(fields.Datetime.from_string(str(self.date_to)), time.max))
            for i in range(delta.days):
                day = start_date + timedelta(days=i)
                expenses = self.env['hr.expense'].search(
                    [('employee_id', '=', employee.id), ('date', '=', day)]).total_amount
            intervals = employee.list_work_time_per_day(date_from, date_to, calendar=employee.resource_calendar_id)
            for rec in intervals:
                attendances = self.env['hr.attendance'].search(
                    [('employee_id', '=', employee.id), ('check_in', '>=', rec[0]), ('check_in', '<=', rec[0])])

                new_date = (rec[0])
                leaves = self.env['hr.leave'].search(
                    [('employee_id', '=', employee.id), '|',
                     ('request_date_from', '=', new_date),
                     ('request_date_from', '=', new_date)])

                if attendances:
                    present += 1
                else:
                    absent += 1
                if leaves:
                    leave += 1
                if expenses:
                    expense += expenses
            datas.append({
                'id': employee.id,
                'name': employee.name,
                'present': present,
                'absent': absent,
                'leave': leave,
                'expense': expense,
                'department': employee.department_id.name
            })
        data = {
            'employee_id': self.employee_ids.ids,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'form': datas,
            'customer_form': customer_datas,
            'customer_check': self.customer_check,

        }
        return self.env.ref('employee_ext.employee_ext_excel_report').report_action(self, data=data)

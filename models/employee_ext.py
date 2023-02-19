# -*- coding: utf-8 -*-

from odoo import models, fields, api


class EmployeeExt(models.Model):
    _name = 'employee.ext'
    _description = 'Employee Extension Report module'

    employee_id = fields.Many2one('hr.employee', string='Employee Name')
    department_id = fields.Many2one('hr.department', string="Department Name")
    date_from = fields.Date(string='Start Date')
    date_to = fields.Date(string='End Date')

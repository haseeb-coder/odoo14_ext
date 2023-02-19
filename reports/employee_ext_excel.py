from datetime import datetime, timedelta
import io
import base64

import xlsxwriter
from docutils.nodes import date
from odoo import api, models, fields
from six import BytesIO
from xlrd import sheet
from xlsxwriter import workbook


class EmployeePdfReport(models.AbstractModel):
    _name = 'report.employee_ext.employee_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, docs):
        sheet = workbook.add_worksheet('Employees')
        bold = workbook.add_format({'bold': True})
        row = 3
        col = 3
        sheet.set_column('D:N', 30)
        if data['customer_check']:
            sheet.write(row, col, 'customer ID', bold)
            sheet.write(row, col + 1, 'customer Name', bold)
            sheet.write(row, col + 2, 'Number of Leads', bold)
            sheet.write(row, col + 3, 'Total sale order ', bold)
            sheet.write(row, col + 4, 'Total sale invoice', bold)
            sheet.write(row, col + 5, 'Total Purchase order', bold)
            sheet.write(row, col + 6, 'Total Purchase Invoice', bold)
            sheet.write(row, col + 7, 'Total Sale Credit Note', bold)
            sheet.write(row, col + 8, 'Total Purchase Credit Note', bold)
            for rec in data['customer_form']:
                row += 1
                sheet.write(row, col, rec['id'])
                sheet.write(row, col + 1, rec['name'])
                sheet.write(row, col + 2, rec['leads'])
                sheet.write(row, col + 3, rec['sale_order'])
                sheet.write(row, col + 4, rec['purchase'])
                sheet.write(row, col + 5, rec['invoice'])
                sheet.write(row, col + 6, rec['p_invoice'])
                sheet.write(row, col + 7, rec['s_credit'])
                sheet.write(row, col + 8, rec['p_credit'])

        else:

            sheet.write(row, col, 'ID', bold)
            sheet.write(row, col + 1, 'Name', bold)
            sheet.write(row, col + 2, 'Department', bold)
            sheet.write(row, col + 3, 'Present', bold)
            sheet.write(row, col + 4, 'off Days', bold)
            sheet.write(row, col + 5, 'Leaves', bold)
            sheet.write(row, col + 6, 'Expense', bold)
            for rec in data['form']:
                row += 1
                sheet.write(row, col, rec['id'])
                sheet.write(row, col + 1, rec['name'])
                sheet.write(row, col + 2, rec['department'])
                sheet.write(row, col + 3, rec['present'])
                sheet.write(row, col + 4, rec['absent'])
                sheet.write(row, col + 5, rec['leave'])
                sheet.write(row, col + 6, rec['expense'])

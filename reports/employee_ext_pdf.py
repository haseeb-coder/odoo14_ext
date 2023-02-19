from odoo import api, models, fields

class EmployeePdfReport(models.AbstractModel):
    _name = 'report.employee_ext.report_data'

    @api.model
    def _get_report_values(self, data=None, docs=False):
        records = self.env['hr.employee'].search([('id', '=', data['employee_id'])])
        return {
            'doc_ids': self.ids,
            'docs': records,
            'data': data,
        }
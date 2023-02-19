# -*- coding: utf-8 -*-
# from odoo import http


# class EmployeeExt(http.Controller):
#     @http.route('/employee_ext/employee_ext/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/employee_ext/employee_ext/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('employee_ext.listing', {
#             'root': '/employee_ext/employee_ext',
#             'objects': http.request.env['employee_ext.employee_ext'].search([]),
#         })

#     @http.route('/employee_ext/employee_ext/objects/<model("employee_ext.employee_ext"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('employee_ext.object', {
#             'object': obj
#         })

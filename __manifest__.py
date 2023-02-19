# -*- coding: utf-8 -*-
{
    'name': "employee_ext",

    'summary': """Employee extension module for report""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Haseeb ur Rehman",
    'website': "http://www.mountsoultion.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'report_xlsx'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/employee_ext.xml',
        'wizard/employee_ext_wizard.xml',
        'reports/employee_ext_pdf.xml',
        'reports/employee_ext_excel.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

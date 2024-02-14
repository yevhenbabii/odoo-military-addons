# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Military Personell Movement',
    'version': '1.0',
    'summary': 'Manage Military Personell movement, locations, statuses and checks',
    'description': "",
    "author": "Yevhen Babii",
    "website": "https://github.com/yevhenbabii",
    "category": "Human Resources/Employees",
    'depends': [
        'base',
        'hr',
        'generic_location',
        'military_employee',
    ],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/hr_move_type.xml',
        'views/hr_move.xml',
        'views/hr_location.xml',
        'views/hr_employee.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}

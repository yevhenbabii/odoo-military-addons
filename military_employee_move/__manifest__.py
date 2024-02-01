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
    'depends': ['hr',
                'generic_location',
                'military_employee',
                ],
    'data': [
        # 'security/military_employee_move_security.xml',
        # 'security/ir.model.access.csv'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}

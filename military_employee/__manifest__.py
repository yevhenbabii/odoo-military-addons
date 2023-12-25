{
    "name": "Military personel data",
    "summary": """
        Military personel data
        """,
    "author": "Yevhen Babii",
    "website": "",
    "category": "Other",
    "version": "1.0",
    "license": "Other proprietary",
    "depends": ["hr",
                "hr_recruitment",
                "contacts",
                "declension_ua",
                "military_rank",
                "military_job",
                "military_department",
                "report_py3o",
                ],
    "demo": ["demo/hr.employee.csv"],
    "external_dependencies": {
        "python": ["js2py"],
        "javascript": ["shevchenko"],
    },
    "data": ["views/employee_views.xml",
             "views/employee_pivot.xml",
             "report/form5.xml",
             ],
    "assets": {
        "web.assets_backend": [
            "military_employee/static/src/css/*.css",
        ],
    },
}

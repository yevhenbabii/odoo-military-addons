{
    "name": "Military personel data",
    "summary": """
        Military personel data
        """,
    "author": "Yevhen Babii",
    "website": "https://github.com/yevhenbabii",
    "category": "Human Resources/Employees",
    "version": "1.0.1",
    "license": "Other proprietary",
    "depends": [
        "hr",
        "hr_recruitment",
        "contacts",
        "declension_ua",
        "military_rank",
        "military_job",
        "military_department",
        "report_py3o",
    ],
    "demo": [
        "demo/hr.employee.csv"
    ],
    "data": [
        "views/employee_views.xml",
        "views/employee_pivot.xml",
        "report/form5.xml",
    ],
    "sequence": '0',
    "assets": {
        "web.assets_backend": [
            "military_employee/static/src/css/*.css",
        ],
    },
}

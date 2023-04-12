{
    "name": "Military Staff Data",
    "summary": """
        Military Staff Data
        """,
    "author": "Yevhen Babii",
    "website": "",
    "category": "Other",
    "version": "14.0.2",
    "license": "Other proprietary",
    "depends": ["hr",
                "military_rank",
                "military_job",
                "military_department",
                ],
    "demo": ["demo/hr.employee.csv"],
    # "external_dependencies": {
    #     "python": ["js2py"],
    #     "javascript": ["shevchenko"],
    # },
    "data": ["views/employee_views.xml",
             "views/employee_pivot.xml",
             "views/assets.xml"
             ],
}

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
    "depends": ["base", "hr", "military_ranks", "military_department", "report_xlsx"],
    "external_dependencies": {
        "python": ["js2py"],
        "javascript": ["shevchenko"],
    },
    "data": ["views/employee_views.xml",
             "views/employee_pivot.xml",
             "views/assets.xml"
             ],
}

{
    "name": "Military Departments",
    "version": "1.0",
    "author": "Yevhen Babii",
    "maintainer": "Yevhen Babii",
    "website": "",
    "license": "Other proprietary",
    "category": "Other",
    "summary": "Departments improvement in HR",
    "depends": ["hr",
                "military_company",
                "declension_ua"],
    "data": ["security/ir.model.access.csv",
             "views/department_views.xml",
             "report/staff_report.xml",
             "report/bchs.xml",
             "data/hr.department.tag.csv"
             ],
    "demo": [
        "demo/hr.department.csv"
    ],
    "installable": True,
}

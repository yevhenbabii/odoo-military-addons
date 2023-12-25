{
    "name": "Military Job Data",
    "version": "1.0",
    "author": "Yevhen Babii",
    "maintainer": "Yevhen Babii",
    "website": "https://github.com/yevhenbabii",
    "license": "Other proprietary",
    "category": "Human Resources",
    "summary": "Military Jobs Improvements",
    "depends": ["hr",
                "hr_recruitment",
                "military_rank",
                "military_department",
                "declension_ua"
                ],
    "data": [
        "security/groups.xml",
        "security/ir.model.access.csv",
        "views/military_job_views.xml",
        "views/military_job_transfer_views.xml"],
    "demo": ["demo/hr.job.csv"],
    "installable": True,
}

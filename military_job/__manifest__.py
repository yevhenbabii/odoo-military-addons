{
    "name": "Military Job Data",
    "version": "14.0.1",
    "author": "Yevhen Babii",
    "maintainer": "Yevhen Babii",
    "website": "https://github.com/yevhenbabii",
    "license": "Other proprietary",
    "category": "Human Resources",
    "summary": "Military Jobs Improvements",
    "depends": ["hr",
                "military_rank",
                "military_department"
                ],
    "data": [
        "security/groups.xml",
        "security/ir.model.access.csv",
        "views/military_job_views.xml",
        "views/military_job_transfer_views.xml"],
    "demo": ["demo/hr.job.csv"],
    "installable": True,
}

# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Employee Job Transfer",
    "category": "HR",
    "version": "14.0.1.0.0",
    "images": ["static/src/img/main_screenshot.png"],
    "author": "Yevhen Babii",
    "license": "AGPL-3",
    "website": "https://github.com/yevhenbabii",
    "depends": [
        "base_setup",
        "hr",
        # "hr_contract_status",
    ],
    "data": [
        "security/groups.xml",
        "security/ir.model.access.csv",
        "data/hr_transfer_cron.xml",
        "data/hr_transfer_data.xml",
        "views/hr_transfer_view.xml",
    ],
    "installable": True,
}

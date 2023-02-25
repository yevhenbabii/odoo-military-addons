from odoo import models, fields


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    reward_line_ids = fields.One2many('hr.employee.reward.line',
                                      'employee_id',
                                      string="Reward History")

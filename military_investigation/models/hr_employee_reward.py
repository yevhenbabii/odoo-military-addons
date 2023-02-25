from odoo import models, fields


class EmployeeReward(models.Model):
    _name = 'hr.employee.reward'
    _description = 'Employee Reward'
    _order = 'priority name'

    name = fields.Char(string="Name")
    image = fields.Image(string="Image")
    priority = fields.Integer(string="Priority")
    category = fields.Selection([
        ('state', 'state'),
        ('department', 'department'),
        ('unit', 'unit')
    ], groups="hr.group_hr_manager")
    # line_ids = fields.Many2one('hr.employee', string="Employee")
    line_ids = fields.One2many('hr.employee.reward.line', 'reward_id', string="Badge History")


class EmployeeRewardApplication(models.Model):
    _name = 'hr.employee.reward.application'
    _description = 'Reward Application'
    _order = 'sequence desc'

    name = fields.Char('Application Reference',
                       required=True,
                       index=True,
                       copy=False,
                       default='New')
    category = fields.Selection(
        'Category',
        index=True, related='hr.employee.reward', store=True)
    author = fields.One2many('hr.employee', 'name', string="Author")
    partner = fields.One2many('res.partner', 'name', string="Partner")
    issue_date = fields.Date(string="Issue Date")
    issue_number = fields.Char(string="Issue Number")
    line_ids = fields.One2many('hr.employee.reward.line', 'reward_id', string="Badge History")


class EmployeeRewardLine(models.Model):
    _name = "hr.employee.reward.line"
    _description = "Employee Reward Lines"

    date = fields.Date(string="Date")
    number = fields.Char(string="Number")
    reward_id = fields.Many2one('hr.employee.reward', string="Reward")
    employee_id = fields.Many2one('hr.employee', string="Employee")
    status = fields.Selection([
        ('draft', 'state'),
        ('confirmed', 'department'),
        ('canceled', 'unit'),
        ('issued', 'issued'),
        ('available', 'available'),
        ('handed', 'handed')])
    text = fields.Text(string="Application Text")

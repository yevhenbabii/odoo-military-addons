from odoo import models, fields, api


class MilitaryRank(models.Model):
    _name = "military.rank"
    _description = "Military Ranks"
    _order = "sequence"
    _avoid_quick_create = True

    active = fields.Boolean('Active', default=True)
    sequence = fields.Integer(string="Sequence", required=True)
    name = fields.Char(string="Name", required=True, index=True, translate=True)
    category = fields.Selection([
        ('private', 'private'),
        ('sergeant', 'sergeant'),
        ('officer', 'officer')
    ], groups="hr.group_hr_manager")
    subcategory = fields.Selection([
        ('junior', 'junior'),
        ('senior', 'senior'),
        ('master', 'master')
    ], groups="hr.group_hr_manager")
    name_short = fields.Char(string="Shortname")
    nato_code = fields.Char(string="Nato Rank Code")
    description = fields.Text('Description')


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    _display_name = 'complete_name'
    _order = 'rank desc'

    rank = fields.Many2one('military.rank',
                           string='Military Rank',
                           groups="hr.group_hr_user",
                           help='Current serviceman military rank')
    rank_category = fields.Selection(
        'Rank Category',
        index=True,
        related='rank.category',
        compute_sudo=True,
        store=True,
        readonly=True)
    complete_name = fields.Char('Complete Name',
                                compute='_compute_complete_name',
                                store=True)

    @api.depends("name", "rank", "rank.name", "complete_name")
    def _compute_complete_name(self):
        for emp in self:
            emp.complete_name = emp.name
            if emp.rank:
                emp.complete_name = '%s %s' % (
                    emp.rank.name,
                    emp.name)
            else:
                emp.complete_name = emp.name


class Job(models.Model):
    _inherit = "hr.job"
    _display_name = "complete_name"
    rank = fields.Many2one('military.rank', string="Job Rank")
    rank_category = fields.Selection(
        'Rank Category',
        index=True,
        related='rank.category',
        compute_sudo=True,
        store=True,
        readonly=True)

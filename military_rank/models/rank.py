from odoo import models, fields, api, _


class MilitaryRank(models.Model):
    _name = "military.rank"
    _description = "Military Ranks"
    _rec_name = "name"
    _order = "sequence asc"
    _avoid_quick_create = True

    active = fields.Boolean("Active", default=True)
    sequence = fields.Integer(string="Sequence", required=True)
    name = fields.Char(string="Name", store=True, required=True, index=True, translate=True)
    name_gent = fields.Char(string="Name Genitive",
                            help="Name in genitive declention (Whom/What)",
                            store=True,
                            required=True)
    name_datv = fields.Char(string="Name Dative",
                            help="Name in dative declention (for Whom/ for What)",
                            store=True,
                            required=True)
    name_ablt = fields.Char(string="Name Ablative",
                            help="Name in ablative declention (by Whom/ by What)",
                            store=True,
                            required=True)

    @api.depends('name')
    def _get_declension(self):
        declension_ua_model = self.env['declension.ua']
        grammatical_cases = ['gent', 'datv', 'ablt']
        for record in self:
            inflected_fields = declension_ua_model.get_declension_fields(record, grammatical_cases)
            for field, value in inflected_fields.items():
                setattr(record, field, value)

    category = fields.Selection([
        ("private", "private"),
        ("sergeant", "sergeant"),
        ("officer", "officer")
    ], groups="hr.group_hr_manager")
    subcategory = fields.Selection([
        ("junior", "junior"),
        ("senior", "senior"),
        ("master", "master")
    ], groups="hr.group_hr_manager")
    name_short = fields.Char(string="Shortname")
    nato_code = fields.Char(string="Nato Rank Code")
    description = fields.Text("Description")
    parent_id = fields.Many2one("military.rank", string="Parent Rank", store=True)


class HrEmployee(models.Model):
    _inherit = "hr.employee"
    _order = "rank_id desc"

    rank_id = fields.Many2one("military.rank",
                              string="Military Rank",
                              groups="hr.group_hr_user",
                              help="Current serviceman military rank",
                              required=True,
                              tracking=True
                              )
    rank_category = fields.Selection(related="rank_id.category", string="Rank Category", store=True)


class Job(models.Model):
    _inherit = "hr.job"
    _display_name = "complete_name"

    rank_id = fields.Many2one("military.rank", string="Job Rank")
    rank_category = fields.Selection(related="rank_id.category", string="Rank Category", store=True)

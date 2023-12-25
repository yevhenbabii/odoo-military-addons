from odoo import fields, models, api


class Company(models.Model):
    _name = "res.company"
    _inherit = "res.company"
    _description = "Description"

    complete_name = fields.Char('Complete Name',
                                compute='_compute_complete_name',
                                store=True)
    name_gent = fields.Char(string="Name gent",
                            compute="_get_declension",
                            help="Name in gent declention (Whom/What)",
                            store=True)
    name_datv = fields.Char(string="Name Dative",
                            compute="_get_declension",
                            help="Name in dative declention (for Whom/ for What)",
                            store=True)
    name_ablt = fields.Char(string="Name Ablative",
                            compute="_get_declension",
                            help="Name in ablative declention (by Whom/ by What)",
                            store=True)

    @api.depends('name')
    def _get_declension(self):
        declension_ua_model = self.env['declension.ua']
        grammatical_cases = ['gent', 'datv', 'ablt']
        for record in self:
            inflected_fields = declension_ua_model.get_declension_fields(record, grammatical_cases)
            for field, value in inflected_fields.items():
                setattr(record, field, value)

    public_name = fields.Char('Public Name', store=True)
    public_name_gent = fields.Char('Public Name gent', store=True)
    public_shortname = fields.Char('Public Shortname', store=True)
    code = fields.Char('Code', store=True)
    commandor = fields.Many2one('hr.job', 'Commandor')

    # staff_chief = fields.Many2one('hr.job', 'Chief of Staff')
    # staff_dep_chief = fields.Many2one('hr.job', 'Commandor')
    # staff_dep_chief = fields.Many2one('hr.job', 'Commandor')

    @api.depends("name", "code")
    def _compute_complete_name(self):
        for company in self:
            name = company.name
            if not company.code:
                company.name = name
            else:
                company.complete_name = 'військова частина ' + company.code

    @api.depends("code", "name_gent")
    def _compute_complete_name_gent(self):
        for company in self:
            name_gent = company.name_gent
            if not company.code:
                company.name_gent = name_gent
            else:
                company.name_gent = 'військової частини ' + company.code

    @api.depends("code", "name_dative")
    def _compute_complete_name_dative(self):
        for company in self:
            name_dative = company.name_dative
            if not company.code:
                company.name_dative = name_dative
            else:
                company.name_dative = 'військовій частині ' + company.code

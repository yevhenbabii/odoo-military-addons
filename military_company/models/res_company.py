from odoo import fields, models, api


class Company(models.Model):
    _name = "res.company"
    _inherit = "res.company"
    _description = "Description"

    complete_name = fields.Char('Complete Name',
                                compute='_compute_complete_name',
                                store=True)
    name_genitive = fields.Char('Genitive Name',
                            compute='_compute_complete_name_genitive',
                            store=True)
    name_dative = fields.Char('Dative Name',
                              compute='_compute_complete_name_dative',
                              store=True)
    public_name = fields.Char('Public Name', store=True)
    public_name_genitive = fields.Char('Public Name Genitive', store=True)
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

    @api.depends("code", "name_genitive")
    def _compute_complete_name_genitive(self):
        for company in self:
            name_genitive = company.name_genitive
            if not company.code:
                company.name_genitive = name_genitive
            else:
                company.name_genitive = 'військової частини ' + company.code

    @api.depends("code", "name_dative")
    def _compute_complete_name_dative(self):
        for company in self:
            name_dative = company.name_dative
            if not company.code:
                company.name_dative = name_dative
            else:
                company.name_dative = 'військовій частині ' + company.code

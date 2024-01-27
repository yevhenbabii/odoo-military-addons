from odoo import fields, models, api


class Company(models.Model):
    _name = "res.company"
    _inherit = "res.company"
    _description = "Description"

    name_gent = fields.Char(string="Name gent",
                            compute="_get_declension",
                            help="Name in genitive declension (Whom/What)",
                            readonly=False,
                            store=True)
    name_datv = fields.Char(string="Name Dative",
                            compute="_get_declension",
                            help="Name in dative declension (for Whom/ for What)",
                            readonly=False,
                            store=True)
    name_ablt = fields.Char(string="Name Ablative",
                            compute="_get_declension",
                            help="Name in ablative declension (by Whom/ by What)",
                            readonly=False,
                            store=True)
    public_name = fields.Char('Public Name', store=True)
    public_name_gent = fields.Char('Public Name gent', store=True)
    public_shortname = fields.Char('Public Shortname', store=True)
    code = fields.Char('Code', store=True)
    commandor = fields.Many2one('hr.job', 'Commandor')
    staff_chief = fields.Many2one('hr.job', 'Chief of Staff')

    @api.depends('name')
    def _get_declension(self):
        declension_ua_model = self.env['declension.ua']
        grammatical_cases = ['gent', 'datv', 'ablt']
        for record in self:
            inflected_fields = declension_ua_model.get_declension_fields(record, grammatical_cases)
            for field, value in inflected_fields.items():
                setattr(record, field, value)

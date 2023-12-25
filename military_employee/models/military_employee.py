import logging, datetime

from odoo import api, fields, models
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

UPDATE_PARTNER_FIELDS = ["name", "user_id", "address_home_id"]


class HrEmployee(models.Model):
    _inherit = "hr.employee"
    # _rec_name = "complete_name"  # ToDo try to implement

    job_id = fields.Many2one('hr.job', string='Job Position',
                             domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    job_title = fields.Char("Job Title", related="job_id.complete_name")
    department_id = fields.Many2one(related="job_id.department_id", store=True, readonly=True)
    parent_id = fields.Many2one(related="department_id.manager_id", store=True, readonly=True)
    last_name = fields.Char("Last Name", required=True, tracking=True)
    first_name = fields.Char("First Name", required=True, tracking=True)
    middle_name = fields.Char("Middle Name", required=True, tracking=True)
    service_type = fields.Selection([
        ('mobilised', 'Mobilised'),
        ('contract', 'Contract'),
        ('regular', 'Regular'),
    ], string='Service Type', default='mobilised', required=True,
        help="The personell service type")
    state = fields.Selection(
        [("field", "Field"),
         ("duty", "Duty"),
         ("trip", "Trip"),
         ("holiday", "Holiday"),
         ("deserter", "Deserter"),
         ("fugitive", "Fugitive"),
         ("refusal", "Refusal"),
         ("hospital", "Hospital"),
         ("hostage", "Hostage"),
         ("missing", "Missing"),
         ("on_shield", "On Shield")],
        required=True,
        default="duty",
        index=True,
        store=True,
        tracking=True
    )
    conscription_place = fields.Many2one("res.partner", "Conscription Place", tracking=True)
    conscription_date = fields.Date("Conscription Date", tracking=True)
    age = fields.Integer(string="Age", compute='_compute_age')
    blood_type_ab = fields.Selection(
        string="Blood Type (ABO)",
        selection=[
            ("a", "A"),
            ("b", "B"),
            ("ab", "AB"),
            ("o", "O"),
        ],
    )
    blood_type_rh = fields.Selection(
        string="Blood Type (Rh)",
        selection=[
            ("+", "+"),
            ("-", "-"),
        ],
    )
    complete_name = fields.Char("Complete Name",
                                compute="_compute_complete_name",
                                store=True,
                                tracking=True)

    @api.depends("name", "rank_id", "job_title")
    def _compute_complete_name(self):
        for record in self:
            rank = record.rank_id.name if record.rank_id else ''
            name = record.name if record.name else ''
            job = record.job_title[0].lower() + record.job_title[1:] if record.job_title else ''
            record.complete_name = f"{rank} {name} {job}" if any([rank, name, job]) else ""

    @api.depends("birthday")
    def _compute_age(self):
        for rec in self:
            rec.age = relativedelta(datetime.date.today(), rec.birthday).years

    name_gent = fields.Char(string="Name Genitive",
                            compute="_get_declension",
                            help="Name in genitive declention (Whom/What)",
                            store=True)
    name_datv = fields.Char(string="Name Dative",
                            compute="_get_declension",
                            help="Name in dative declention (for Whom/ for What)",
                            store=True)
    name_ablt = fields.Char(string="Name Ablative",
                            compute="_get_declension",
                            help="Name in ablative declention (by Whom/ by What)",
                            store=True)
    last_name_gent = fields.Char(string="Last Name Genitive",
                                 compute="_get_declension",
                                 help="Last name in genitive declention (Whom/What)",
                                 store=True)
    last_name_datv = fields.Char(string="Last Name Dative",
                                 compute="_get_declension",
                                 help="Last name in dative declention (for Whom/ for What)",
                                 store=True)
    last_name_ablt = fields.Char(string="Last Name Ablative",
                                 compute="_get_declension",
                                 help="Last name in ablative declention (by Whom/ by What)",
                                 store=True)

    first_name_gent = fields.Char(string="First Name Genitive",
                                  compute="_get_declension",
                                  help="First name in genitive declention (Whom/What)",
                                  store=True)
    first_name_datv = fields.Char(string="First Name Dative",
                                  compute="_get_declension",
                                  help="First name in dative declention (for Whom/ for What)",
                                  store=True)
    first_name_ablt = fields.Char(string="First Name Ablative",
                                  compute="_get_declension",
                                  help="First name in ablative declention (by Whom/ by What)",
                                  store=True)

    middle_name_gent = fields.Char(string="Middle Name Genitive",
                                   compute="_get_declension",
                                   help="Middle name in genitive declention (Whom/What)",
                                   store=True)
    middle_name_datv = fields.Char(string="Middle Name Dative",
                                   compute="_get_declension",
                                   help="Middle name in dative declention (for Whom/ for What)",
                                   store=True)
    middle_name_ablt = fields.Char(string="Middle Name Ablative",
                                   compute="_get_declension",
                                   help="Middle name in ablative declention (by Whom/ by What)",
                                   store=True)

    @api.depends('name', 'first_name', 'middle_name', 'last_name')
    def _get_declension(self):
        declension_ua_model = self.env['declension.ua']
        grammatical_cases = ['gent', 'datv', 'ablt']
        for record in self:
            inflected_fields = declension_ua_model.get_declension_fields(record, grammatical_cases)
            for field, value in inflected_fields.items():
                setattr(record, field, value)

    @api.model
    def _get_name(self, last_name, first_name, middle_name):
        return " ".join(p for p in (last_name, first_name, middle_name) if p)

    @api.onchange("last_name", "first_name", "middle_name")
    def _onchange_name(self):
        self.last_name = self.last_name.title() if self.last_name else ''
        self.first_name = self.first_name.title() if self.first_name else ''
        self.middle_name = self.middle_name.title() if self.middle_name else ''
        self.name = self._get_name(self.last_name, self.first_name, self.middle_name)

    def _prepare_vals_on_create(self, vals):
        if any([vals.get(field) for field in ["first_name", "last_name", "middle_name"]]):
            vals["name"] = self._get_name(vals.get("last_name"), vals.get("first_name"),
                                          vals.get("middle_name"))
        else:
            raise ValidationError("No name set on create.")

    def _prepare_vals_on_write(self, vals):
        if any([vals.get(field) for field in ["first_name", "last_name", "middle_name"]]):
            # last_name = vals.get("last_name", self.last_name)
            # first_name = vals.get("first_name", self.first_name)
            # middle_name = vals.get("middle_name", self.middle_name)
            vals["name"] = self._get_name(self.last_name, self.first_name, self.middle_name)
        # else:
        #     raise ValidationError("No name set on write.")

    @api.model
    def create(self, vals):
        self._prepare_vals_on_create(vals)
        res = super().create(vals)
        return res

    def write(self, vals):
        self._prepare_vals_on_write(vals)
        res = super().write(vals)
        return res

import logging
# import js2py
from odoo import api, fields, models
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
import datetime

_logger = logging.getLogger(__name__)


# UPDATE_PARTNER_FIELDS = ["lastname", "firstname", "middlename", "user_id", "address_home_id"]


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    #temp_job_id = fields.Many2one('hr.job', 'temp_employee_id', string='Temporary Job Position', store=True)
    job_id = fields.Many2one('hr.job', string='Job Position',
                             domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    department_id = fields.Many2one(related="job_id.department_id", store=True, readonly=True)
    parent_id = fields.Many2one(related="department_id.manager_id", store=True, readonly=True)
    lastname = fields.Char("Last Name", tracking=True)
    firstname = fields.Char("First Name", tracking=True)
    middlename = fields.Char("Middlename", tracking=True)
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

    @api.depends("birthday")
    def _compute_age(self):
        for rec in self:
            rec.age = relativedelta(datetime.date.today(), rec.birthday).years

    # name_dative = fields.Char(compute="_get_declention", store="True", string="Name Dative")

    # firstname_dative = fields.Char(compute="_get_declention", string="Firstname Dative")
    # name_accusative = fields.Char(compute="_get_declention", store=True)
    # name_ablative = fields.Char(compute="_get_declention", store=True)
    # name_locative = fields.Char(compute="_get_declention", store=True)
    # name_vocative = fields.Char(compute="_get_declention", store=True)
    # shevchenko = js2py.require("shevchenko")

    # @api.model
    # # ("gender", "firstname", "middlename", "lastname")
    # def _get_declention(self):
    #     for res in self:
    #         shevchenko = js2py.require("shevchenko")
    #         anthroponym = {
    #             "gender": self.gender,
    #             "firstName": self.firstname,
    #             "middleName": self.middlename,
    #             "lastName": self.lastname
    #         }
    #         if self.gender and self.firstname:
    #             res.name_dative = "%s %s %s" % ((shevchenko.inDative(anthroponym)["lastName"]),
    #                                             (shevchenko.inDative(anthroponym)["firstName"]),
    #                                             (shevchenko.inDative(anthroponym)["middleName"]))

    # self.name_accusative = "%s %s %s" % (shevchenko.inAccusative(anthroponym)["lastName"],
    #                                      shevchenko.inAccusative(anthroponym)["firstName"],
    #                                      shevchenko.inAccusative(anthroponym)["middleName"])
    # self.name_ablative = "%s %s %s" % (shevchenko.inAblative(anthroponym)["lastName"],
    #                                    shevchenko.inAblative(anthroponym)["firstName"],
    #                                    shevchenko.inAblative(anthroponym)["middleName"])
    # self.name_locative = "%s %s %s" % (shevchenko.inLocative(anthroponym)["lastName"],
    #                                    shevchenko.inLocative(anthroponym)["firstName"],
    #                                    shevchenko.inLocative(anthroponym)["middleName"])
    # self.name_vocative = "%s %s %s" % (shevchenko.inVocative(anthroponym)["lastName"],
    #                                    shevchenko.inVocative(anthroponym)["firstName"],
    #                                    shevchenko.inVocative(anthroponym)["middleName"])

    # class HrEmployee(models.Model):
    #     _inherit = "hr.employee"

    # @api.onchange("job_id", "department_id", "parent_id")
    # def _onchange_job(self):
    #     if self.job_id or self.department_id or self.parent_id:
    #         self.department_id = self.job_id.department_id
    #         self.complete_name = self._compute_complete_name()
    #         self.parent_id = self.department_id.manager_id

    @api.depends("job_id")
    def _compute_job_title(self):
        for employee in self.filtered("job_id"):
            employee.job_title = employee.job_id.complete_name

    @api.model
    def _get_name(self, lastname, firstname, middlename):
        return " ".join(p for p in (lastname, firstname, middlename) if p)

    @api.onchange("lastname", "firstname", "middlename")
    def _onchange_name(self):
        if self.firstname or self.lastname or self.middlename:
            self.name = self._get_name(self.lastname, self.firstname, self.middlename)

    def _prepare_vals_on_create(self, vals):
        if vals.get("firstname") or vals.get("lastname") or vals.get("middlename"):
            vals["name"] = self._get_name(vals.get("lastname"), vals.get("firstname"),
                                          vals.get("middlename"))
        elif vals.get("name"):
            vals["lastname"] = self.split_name(vals["name"])["lastname"]
            vals["firstname"] = self.split_name(vals["name"])["firstname"]
            vals["middlename"] = self.split_name(vals["name"])["middlename"]
        else:
            raise ValidationError(("No name set."))

    def _prepare_vals_on_write(self, vals):
        if "firstname" in vals or "lastname" in vals or "middlename" in vals:
            if "lastname" in vals:
                lastname = vals.get("lastname")
            else:
                lastname = self.lastname
            if "firstname" in vals:
                firstname = vals.get("firstname")
            else:
                firstname = self.firstname
            if "middlename" in vals:
                middlename = vals.get("middlename")
            else:
                middlename = self.middlename
            vals["name"] = self._get_name(lastname, firstname, middlename)
        elif vals.get("name"):
            vals["lastname"] = self.split_name(vals["name"])["lastname"]
            vals["firstname"] = self.split_name(vals["name"])["firstname"]
            vals["middlename"] = self.split_name(vals["name"])["middlename"]

    @api.model
    def split_name(self, name):
        clean_name = " ".join(name.split(None)) if name else name
        return self._get_inverse_name(clean_name)

    @api.model
    def create(self, vals):
        self._prepare_vals_on_create(vals)
        res = super().create(vals)
        return res

    def write(self, vals):
        self._prepare_vals_on_write(vals)
        res = super().write(vals)
        return res

    @api.model
    def _get_inverse_name(self, name):
        """Compute the inverted name.

        This method can be easily overriden by other submodules.
        You can also override this method to change the order of name's
        attributes

        When this method is called, :attr:`~.name` already has unified and
        trimmed whitespace.
        """
        # Remove redundant spaces
        name = self._get_whitespace_cleaned_name(name)
        parts = name.split(" ", 1)
        if len(parts) > 1:
            parts = [parts[0], " ".join(parts[1:])]
        else:
            while len(parts) < 2:
                parts.append(False)
        return {"lastname": parts[0], "firstname": parts[1], "middlename": parts[2]}

    @api.model
    def _get_whitespace_cleaned_name(self, name):
        """Remove redundant whitespace from :param:`name`.

        Removes leading, trailing and duplicated whitespace.
        """
        try:
            name = " ".join(name.split()) if name else name
        except UnicodeDecodeError:
            name = " ".join(name.decode("utf-8").split()) if name else name
        return name

    def _split_part(self, name_part, name_split):
        """Split a given part of a name.

        :param name_split: The parts of the name
        :type dict

        :param name_part: The part to split
        :type str
        """
        name = name_split.get(name_part, False)
        parts = name.split(" ", 1) if name else []
        if not name or len(parts) < 2:
            return False
        return parts

    # TODO need to fix due to errors
    def _inverse_name(self):
        """Try to revert the effect of :method:`._compute_name`."""
        for record in self:
            parts = self._get_inverse_name(record.name)
            record.write(
                {
                    "lastname": parts["lastname"],
                    "firstname": parts["firstname"],
                    "middlename": parts["middlename"],
                }
            )

    @api.model
    def _install_military_employee(self):
        """Save names correctly in the database.

        Before installing the module, field ``name`` contains all full names.
        When installing it, this method parses those names and saves them
        correctly into the database. This can be called later too if needed.
        """
        # Find records with empty firstname and lastname
        records = self.search([
            ("lastname", "=", False),
            ("firstname", "=", False),
            ("middlename", "=", False)
        ])

        # Force calculations there
        records._inverse_name()
        _logger.info("%d employees updated installing module.", len(records))

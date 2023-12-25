from odoo import fields, models, api
import js2py


class Shevchenko(models.AbstractModel):
    _name = 'shevchenko'
    _description = 'Description'

    name_gent = fields.Char(compute="_shevchenko_declension", store=True, string="Name Genitive")
    name_datv = fields.Char(compute="_shevchenko_declension", store=True, string="Name Dative")
    name_ablt = fields.Char(compute="_shevchenko_declension", store=True, string="Name Ablative")
    shevchenko = js2py.require("shevchenko")

    @api.onchange ("gender", "first_name", "middle_name", "last_name")
    def _shevchenko_declension(self):
        for res in self:
            shevchenko = js2py.require("shevchenko")
            anthroponym = {
                "gender": self.gender,
                "lastName": self.last_name,
                "firstName": self.first_name,
                "middleName": self.middle_name,
            }
            if self.gender and self.first_name and self.last_name and self.middle_name:
                res.name_gent = "%s %s %s" % ((shevchenko.inGenitive(anthroponym)["lastName"]),
                                                (shevchenko.inGenitive(anthroponym)["firstName"]),
                                                (shevchenko.inGenitive(anthroponym)["middleName"]))
                res.name_datv = "%s %s %s" % ((shevchenko.inDative(anthroponym)["lastName"]),
                                                (shevchenko.inDative(anthroponym)["firstName"]),
                                                (shevchenko.inDative(anthroponym)["middleName"]))
                res.name_ablt = "%s %s %s" % ((shevchenko.inAblative(anthroponym)["lastName"]),
                                                (shevchenko.inAblative(anthroponym)["firstName"]),
                                                (shevchenko.inAblative(anthroponym)["middleName"]))

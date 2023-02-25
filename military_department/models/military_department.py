from odoo import fields, models, api
from odoo.osv import expression


class DepartmentTag(models.Model):
    _name = "hr.department.tag"
    _description = "Department Tag"

    name = fields.Char(required=True)
    code = fields.Char()
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ("name_unique", "unique(name)", "Name must be unique!"),
        ("code_unique", "unique(code)", "Code must be unique!")
    ]


class Department(models.Model):
    _inherit = "hr.department"
    _order = "level asc, sequence asc, name asc"
    _display_name = "complete_name"

    sequence = fields.Integer(default=1)
    tag_ids = fields.Many2many("hr.department.tag", 'hr_department_tag_rel', string="Tags")
    complete_name = fields.Char("Complete Name",
                                compute="_compute_complete_name",
                                store=True)
    child_ids = fields.One2many("hr.department", "parent_id", "Contains")
    user_ids = fields.Many2many('res.users', 'hr_department_users_rel', 'did', 'user_id',
                                string='Accepted Users')
    code = fields.Char("Code",
                       compute="_department_code",
                       store=True,
                       readonly=False)
    level = fields.Integer(
        string="Level",
        compute="_compute_level",
        store=True,
        recursive=True
    )

    name_genitive = fields.Char("Genitive Name", store=True)
    name_accusative = fields.Char("Accusative Name")
    name_ablative = fields.Char("Ablative Name")
    complete_name_genitive = fields.Char("Complete Name Genitive",
                                         compute="_compute_complete_name_genitive",
                                         store=True,
                                         recursive=True
                                         )

    @api.depends("level", "parent_id.level")
    def _compute_level(self):
        for dep in self:
            dep.level = dep.level
            if dep.parent_id:
                dep.level = dep.parent_id.level + 1
            else:
                dep.level = 1

    def name_get(self):
        res = []
        for dep in self:
            if dep.code:
                name = "[%(code)s %(company)s] %(complete_name)s" % {"code": dep.code,
                                                                     "complete_name": dep.complete_name.upper(),
                                                                     "company": dep.company_id.code}
            else:
                name = "[%s] %s" % (dep.company_id.code, dep.complete_name.upper())
            res.append((dep.id, name.upper()))
        return res

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        args = args or []
        domain = []
        if name:
            domain = ["|", ("code", "=ilike", name + "%"), ("name", operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ["&", "!"] + domain[1:]
        departments = self.search(domain + args, limit=limit)
        return departments.name_get()

    @api.depends("name", "name_genitive", "parent_id.complete_name_genitive",
                 "company_id.name_genitive")
    def _department_code(self):
        for dep in self:
            dep.code = dep.code
            if not dep.code:
                dep.code = dep.parent_id.code
            else:
                dep.code = dep.code

    @api.depends("name", "name_genitive", "parent_id.complete_name_genitive",
                 "company_id.name_genitive")
    def _compute_complete_name(self):
        for dep in self:
            if dep.parent_id.complete_name_genitive:
                dep.complete_name = "%s %s" % (dep.name,
                                               dep.parent_id.complete_name_genitive)
            else:
                dep.complete_name = "%s %s" % (dep.name, dep.company_id.name_genitive)

    @api.depends("name_genitive",
                 "parent_id.complete_name_genitive",
                 "company_id.name_genitive")
    def _compute_complete_name_genitive(self):
        for dep in self:
            # dep.complete_name_genitive = dep.name_genitive
            if not dep.name_genitive:
                if not dep.parent_id:
                    dep.complete_name_genitive = dep.name_genitive
                else:
                    dep.complete_name_genitive = dep.parent_id.complete_name_genitive
            else:
                if dep.parent_id and dep.parent_id.complete_name_genitive:
                    dep.complete_name_genitive = "%s %s" % (
                        dep.name_genitive,
                        dep.parent_id.complete_name_genitive)
                else:
                    dep.complete_name_genitive = "%s %s" % (dep.name_genitive,
                                                            dep.company_id.name_genitive)

    @api.onchange("name", "name_genitive", "parent_id")
    def _onchange_department_name(self):
        if self.name or self.parent_id or self.name_genitive:
            self._compute_complete_name()
            self._compute_complete_name_genitive()
            self._department_code()


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    department_level = fields.Integer('Level', store='True', related='department_id.level')

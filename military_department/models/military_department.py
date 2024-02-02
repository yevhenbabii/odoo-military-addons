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
    # _display_name = "complete_name"
    _avoid_quick_create = True

    sequence = fields.Integer(default=1)
    tag_ids = fields.Many2many(comodel_name="hr.department.tag",
                               relation='hr_department_tag_rel',
                               string="Tags")
    user_ids = fields.Many2many('res.users',
                                'hr_department_users_rel',
                                'did',
                                'user_id',
                                string='Accepted Users'
                                )
    jobs_ids = fields.One2many('hr.job',
                               compute='_compute_jobs_ids',
                               string='Jobs')
    member_ids = fields.One2many(comodel_name='hr.employee',
                                 compute='_compute_member_ids',
                                 string='Members',
                                 readonly=True,
                                 recursive=True,
                                 )
    code = fields.Char(string="Code",
                       compute="_department_code",
                       store=True,
                       readonly=False)
    level = fields.Integer(
        string="Level",
        compute="_compute_level",
        store=True,
        recursive=True
    )
    commandor_id = fields.Many2one('hr.job',
                                   string='Commandor',
                                   required=True,
                                   tracking=True,
                                   domain="['|', '|', ('company_id', '=', False), ('company_id', '=', company_id), ('department_id', '=', id)]")
    name_gent = fields.Char(string="Name Genitive",
                            compute="_get_declension",
                            help="Name in genitive declension (Whom/What)",
                            store=True)
    name_datv = fields.Char(string="Name Dative",
                            compute="_get_declension",
                            help="Name in dative declension (for Whom/for What)",
                            store=True)
    name_ablt = fields.Char(string="Name Ablative",
                            compute="_get_declension",
                            help="Name in ablative declension (by Whom/by What)",
                            store=True)
    complete_name_gent = fields.Char("Complete Name Genitive",
                                     compute="_compute_complete_name_gent",
                                     store=True,
                                     recursive=True
                                     )

    @api.model
    def _compute_member_ids(self):
        for department in self:
            employees = self.env['hr.employee'].search([
                '|',
                ('department_id', '=', department.id),
                ('department_id', 'child_of', department.id),
            ])
            department.member_ids = employees

    @api.model
    def _compute_child_ids(self):
        for department in self:
            departments = self.env['hr.department'].search([
                '|',
                ('parent_id', '=', department.id),
                ('parent_id', 'child_of', department.id),
            ])
            department.child_ids = departments

    @api.model
    def _compute_jobs_ids(self):
        for department in self:
            jobs = self.env['hr.job'].search([
                '|',
                ('department_id', '=', department.id),
                ('department_id', 'child_of', department.id),
            ])
            department.jobs_ids = jobs

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
                name = "[%s] %s" % (dep.code, dep.complete_name.upper())
            else:
                name = dep.name.upper()
            res.append((dep.id, name))
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

    @api.depends("parent_id", "code")
    def _department_code(self):
        for dep in self:
            dep.code = dep.code
            if not dep.code:
                dep.code = dep.parent_id.code
            else:
                dep.code = dep.code

    @api.depends("name", "name_gent", "parent_id.complete_name_gent",
                 "company_id.name_gent")
    def _compute_complete_name(self):
        for dep in self:
            if dep.parent_id and dep.parent_id.complete_name_gent:
                dep.complete_name = "%s %s" % (dep.name,
                                               dep.parent_id.complete_name_gent)
            else:
                dep.complete_name = "%s %s" % (dep.name, dep.company_id.name_gent)

    @api.depends("name_gent",
                 "parent_id.complete_name_gent",
                 "company_id.name_gent")
    def _compute_complete_name_gent(self):
        for dep in self:
            if not dep.name_gent:
                if not dep.parent_id:
                    dep.complete_name_gent = dep.name_gent
                else:
                    dep.complete_name_gent = dep.parent_id.complete_name_gent
            else:
                if dep.parent_id and dep.parent_id.complete_name_gent:
                    dep.complete_name_gent = "%s %s" % (
                        dep.name_gent,
                        dep.parent_id.complete_name_gent)
                else:
                    dep.complete_name_gent = "%s %s" % (dep.name_gent,
                                                        dep.company_id.name_gent)

    @api.onchange("name", "name_gent", "parent_id")
    def _onchange_department_name(self):
        if self.name or self.parent_id or self.name_gent:
            self._compute_complete_name()
            self._compute_complete_name_gent()
            self._department_code()

    @api.depends('name')
    def _get_declension(self):
        declension_ua_model = self.env['declension.ua']
        grammatical_cases = ['gent', 'datv', 'ablt']
        for record in self:
            inflected_fields = declension_ua_model.get_declension_fields(record, grammatical_cases)
            for field, value in inflected_fields.items():
                setattr(record, field, value)

    total_employee = fields.Integer(string='Total Employee',
                                    compute='_compute_total_employee',
                                    store=False,
                                    recursive=True
                                    )
    total_staff = fields.Integer(string='Total Staff',
                                 compute='_compute_total_employee',
                                 store=False,
                                 recursive=True
                                 )
    total_vacant = fields.Integer(string='Total Vacant',
                                  compute='_compute_total_employee',
                                  store=False,
                                  recursive=True
                                  )

    # TODO Fix calculations
    @api.depends('member_ids', 'child_ids', 'jobs_ids')
    def _compute_total_employee(self):
        for department in self:
            total_employee = len(department.member_ids)
            total_staff = 0
            total_vacant = 0

            for job in department.jobs_ids:
                total_staff += job.no_of_recruitment
                total_vacant += job.expected_employees

            for sub_department in department.child_ids:
                total_employee += sub_department.total_employee
                total_staff += sub_department.total_staff
                total_vacant += sub_department.total_vacant

            department.total_employee += total_employee
            department.total_staff += total_staff
            department.total_vacant += total_vacant


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    department_level = fields.Integer('Level', store='True', related='department_id.level')

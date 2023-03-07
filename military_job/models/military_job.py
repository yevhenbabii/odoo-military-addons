from odoo import fields, models, api


class Job(models.Model):
    _inherit = "hr.job"
    _display_name = "complete_name"
    _order = "level, sequence"

    employee_ids = fields.One2many('hr.employee', 'job_id', string='Employees')
    employee_id = fields.Many2one('hr.employee', string='Employee',
                                  compute='compute_employee',
                                  inverse='inverse_employee', store=True)
    # employee_id = fields.Many2one(string="Employee", comodel_name="hr.employee", compute='_compute_employee', store=True)
    temp_employee_id = fields.Many2one("hr.employee", string='Temporary Employee')
    sequence = fields.Integer(default=1)
    level = fields.Integer('Level', store='True', related='department_id.level')
    complete_name = fields.Char(string='Job Name',
                                store='True',
                                compute='_compute_complete_name',
                                readonly='False')
    mos = fields.Char(string="Job MOS code")
    payroll_grade = fields.Char(string="Payroll Grade")

    @api.depends('employee_ids')
    def compute_employee(self):
        if len(self.employee_ids) > 0:
            self.employee_id = self.employee_ids[0]

    def inverse_employee(self):
        if len(self.employee_ids) > 0:
            # delete previous reference
            employee = self.env['hr.employee'].browse(self.employee_ids[0].id)
            employee.job_id = False
        # set new reference
        self.employee_id.job_id = self

    # @api.depends('employee_ids')
    # def _compute_employee(self):
    #     for job in self:
    #         job.employee_id = job.employee_ids.filtered(lambda x: x.id == job.id)
    #             # self.env['hr.employee'].search([('id', '=', job.employee_ids.ids)], limit=1)
    #
    # def _search_employee(self, operator, value):
    #     return [('employee_id', operator, value)]

    # TODO fix complete_name
    @api.depends("name", "department_id.complete_name_genitive", "company_id.name_genitive")
    def _compute_complete_name(self):
        for job in self:
            job.complete_name = job.name
            if job.name and job.department_id.complete_name_genitive:
                job.complete_name = '%s %s' % (job.name, job.department_id.complete_name_genitive)
            else:
                job.complete_name = '%s %s' % (job.name, job.company_id.name_genitive)

    @api.onchange('name', 'department_id')
    def _onchange_name(self):
        if self.name or self.department_id:
            self._compute_complete_name()

    def name_get(self):
        res = []
        for job in self:
            name = job.complete_name
            res.append((job.id, name))
        return res

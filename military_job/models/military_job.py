from odoo import fields, models, api, _


class Job(models.Model):
    _inherit = "hr.job"
    _display_name = "complete_name"
    _order = "level, sequence"

    # TODO: check behaviour on archiving
    name = fields.Char(string='Job Position', required=True, index='trigram', translate=False)
    name_gent = fields.Char(string="Name Genitive",
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

    active = fields.Boolean('Active', default=True, store=True, readonly=False)
    sequence = fields.Integer(default=1)
    level = fields.Integer('Level', store='True', related='department_id.level')
    complete_name = fields.Char(string='Job Name',
                                store='True',
                                compute='_compute_complete_name',
                                readonly='False')
    mos = fields.Char(string="Job MOS code")
    payroll_grade = fields.Char(string="Payroll Grade")

    # Change sql constraint to have multiple identical job names in one department
    _sql_constraints = [
        ('name_company_uniq', 'unique(name, mos, company_id, department_id)',
         'The name of the job position and MOS must be unique per department in company!'),
    ]

    @api.depends("name", "department_id.complete_name_gent", "company_id.name_gent")
    def _compute_complete_name(self):
        for job in self:
            job.complete_name = job.name
            if job.name and job.department_id.complete_name_gent:
                job.complete_name = '%s %s' % (job.name, job.department_id.complete_name_gent)
            else:
                job.complete_name = '%s %s' % (job.name, job.company_id.name_gent)

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

    @api.depends('no_of_recruitment', 'employee_ids.job_id', 'employee_ids.active')
    def _compute_employees(self):
        employee_data = self.env['hr.employee']._read_group([('job_id', 'in', self.ids)],
                                                            ['job_id'], ['job_id'])
        result = dict((data['job_id'][0], data['job_id_count']) for data in employee_data)
        for job in self:
            job.no_of_employee = result.get(job.id, 0)
            job.expected_employees = job.no_of_recruitment - result.get(job.id, 0)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def _job_count(self):
        for each in self:
            job_ids = self.env['hr.transfer.line'].sudo().search(
                [('employee_id', '=', each.id)])
            each.job_count = len(job_ids)

    def job_view(self):
        self.ensure_one()
        domain = [
            ('employee_id', '=', self.id)]
        return {
            'name': _('Jobs'),
            'domain': domain,
            'res_model': 'hr.transfer.line',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree',
            # 'help': _('''<p class="oe_view_nocontent_create">
            #                Click to assign new job
            #             </p>'''),
            'limit': 80,
            'context': "{'employee_id': %s}" % self.id
        }

    job_count = fields.Integer(compute='_job_count',
                               string='# Jobs')

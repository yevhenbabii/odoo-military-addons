from odoo import fields, models, api


class Job(models.Model):
    _inherit = "hr.job"
    _display_name = "complete_name"
    _order = "level, sequence"

    sequence = fields.Integer(default=1)
    level = fields.Integer('Level', store='True',
                           related='department_id.level')
    complete_name = fields.Char(string='Job Name',
                                store='True',
                                compute='_compute_complete_name',
                                readonly='False')
    mos = fields.Char(string="Job MOS code")
    payroll_grade = fields.Char(string="Payroll Grade")

    # @api.depends('no_of_recruitment', 'employee_ids.job_id', 'employee_ids.active')
    # def _compute_employees(self):
    #     employee_data = self.env['hr.employee'].read_group([('job_id', 'in', self.ids)],
    #                                                         ['job_id'], ['job_id'])
    #     result = dict((data['job_id'][0], data['job_id_count']) for data in employee_data)
    #     for job in self:
    #         job.no_of_employee = result.get(job.id, 0)
    #         job.expected_employees = job.no_of_recruitment - job.no_of_employee

    @api.depends("name", "department_id.complete_name_genitive",
                 "company_id.name_genitive")
    def _compute_complete_name(self):
        for job in self:
            job.complete_name = job.name
            if job.name and job.department_id.complete_name_genitive:
                job.complete_name = '%s %s' % (job.name, job.department_id.complete_name_genitive)
            # else:
            #     job.complete_name = '%s %s' % (job.name, job.company_id.name_genitive)

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

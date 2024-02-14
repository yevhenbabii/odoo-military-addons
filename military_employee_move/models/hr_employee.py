from odoo import fields, models, api, _


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    status_id = fields.Many2one('hr.employee.status')
    location_id = fields.Many2one(
        'hr.work.location',
        "Employee Location",
        compute='_compute_last_move_id',
        readonly=True,
        store=True,
    )
    move_ids = fields.One2many(
        'hr.move.line',
        'employee_id',
        string='Employee Moves'
    )
    last_move_id = fields.Many2one(
        comodel_name='hr.move',
        compute='_compute_last_move_id',
        string='Last Move',
        store=True,
    )
    last_move_date = fields.Datetime(
        compute='_compute_last_move_id',
        string='Last Move Date',
        store=True,
    )

    @api.model
    def _compute_last_move_id(self):
        for employee in self:
            domain = [
                ('employee_id', '=', employee.id),
                ('state', '=', 'done'),
            ]
            last_move_id = self.env['hr.move.line'].search(domain, limit=1, order='date desc')
            employee.last_move_id = last_move_id if last_move_id else False
            employee.last_move_date = last_move_id.date if last_move_id else False
            employee.location_id = last_move_id.location_dest_id if last_move_id else False

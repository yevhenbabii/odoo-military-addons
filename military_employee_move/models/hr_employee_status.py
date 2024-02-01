from odoo import fields, models


class HrEmployeeStatus(models.Model):
    _name = "hr.employee.status"
    _description = "Employee Status"
    _order = 'sequence'

    name = fields.Char(description='Status Name', required=True)
    sequence = fields.Integer(string='Sequence', help='Employee sequence number')
    description = fields.Text(string='Description', help="Status description")
    dest_ids = fields.One2many('hr.employee.status')
    parent_id = fields.Many2one('hr.employee.status')
    child_ids = fields.One2many('hr.employee.status',
                                'child_ids')

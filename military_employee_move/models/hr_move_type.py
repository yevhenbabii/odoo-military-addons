from odoo import fields, models, api


class HrMoveType(models.Model):
    _name = "hr.move.type"
    _description = "Staff Move Type"
    _order = "name asc"

    name = fields.Char(
        'Operation Type',
        required=True
    )
    color = fields.Integer('Color')
    sequence = fields.Integer('Sequence')
    sequence_id = fields.Many2one(
        'ir.sequence',
        'Reference Sequence',
        check_company=True,
        copy=False
    )
    sequence_code = fields.Char(
        'Sequence Prefix',
        required=True
    )
    location_id = fields.Many2one(
        'hr.work.location',
        'Default Destination Location',
        check_company=True,
        help="This is the default destination location when you create a move manually with this operation type."
    )
    code = fields.Selection(
        [('incoming', 'Arrival'),
         ('outgoing', 'Departure'),
         ('internal', 'Internal')
         ], 'Type of Operation',
        required=True
    )
    report_ids = fields.Many2one(
        'ir.actions.report',
        string='Reports',
        domain="[('model', '=', 'hr.move')]"
    )
    description = fields.Text('Description of Move')
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        index=True,
        default=lambda self: self.env.company
    )

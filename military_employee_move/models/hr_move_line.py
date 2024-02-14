from odoo import api, fields, models
from odoo.tools.mail import html2plaintext, is_html_empty


class HrMoveLine(models.Model):
    _name = "hr.move.line"
    _description = "Employee Move"
    _order = 'id asc'

    name = fields.Char('Description',
                       index=True,
                       required=True)
    sequence = fields.Integer('Sequence', default=10)
    create_date = fields.Datetime(
        'Creation Date',
        index=True,
        readonly=True
        )
    date = fields.Date(
        'Move Date',
        related='move_id.date',
        readonly=True,
        index=True,
        required=True
        )
    end_date = fields.Datetime(
        'Move End Date', index=True
        )
    company_id = fields.Many2one(
        'res.company',
        related='move_id.company_id',
        default=lambda self: self.env.company,
        index=True,
        required=True)
    employee_id = fields.Many2one(
        'hr.employee', 'Employee',
        check_company=True,
        # domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        index=True, required=True,
        states={'done': [('readonly', True)]})
    description = fields.Text('Description of Move')
    location_id = fields.Many2one(
        'hr.work.location',
        'Source Location',
        auto_join=True,
        index=True,
    )
    location_dest_id = fields.Many2one(
        'hr.work.location',
        'Destination Location',
        auto_join=True,
        index=True,
        required=True,
        help="Location where the system will locate the Employee."
    )
    partner_id = fields.Many2one(
        'res.partner', 'Source Address',
        states={'done': [('readonly', True)]},
        help="Optional address where Employee is Located")
    partner_dest_id = fields.Many2one(
        'res.partner', 'Destination Address',
        states={'done': [('readonly', True)]},
        help="Optional address where Employee is to be moved")
    move_id = fields.Many2one(
        'hr.move',
        'Transfer',
        index=True,
        states={'done': [('readonly', True)]},
        check_company=True)
    move_partner_id = fields.Many2one(
        'res.partner',
        'Transfer Destination Address',
        related='move_id.partner_id',
        readonly=False)
    note = fields.Text('Notes')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ],
        string='Status',
        copy=False,
        default='draft',
        index=True,
        readonly=True,
        help="* Draft: When the move is created and not yet confirmed.\n"
             "* Done: When the move is processed, the state is \'Done\'.")
    origin = fields.Char("Source Document")  # ToDo Make link to document model
    move_type_id = fields.Many2one('hr.move.type', 'Operation Type', check_company=True)
    inventory_id = fields.Many2one('hr.inventory', 'Inventory', check_company=True)

    def _get_description(self, move_type_id):
        """ return employee move description depending on
        picking type passed as argument.
        """
        self.ensure_one()
        move_code = move_type_id.code
        description = html2plaintext(self.description) if not is_html_empty(
            self.description) else self.name
        if move_code == 'incoming':
            return self.move_type_id.description or self.name
        if move_code == 'outgoing':
            return self.move_type_id.description or self.name
        if move_code == 'internal':
            return self.move_type_id.description or self.name
        return description

    @api.onchange('employee_id', 'move_type_id')
    def onchange_employee(self):
        if self.employee_id:
            self.description = self._get_description(self.move_type_id)
            self.location_id = self.employee_id.location_id or ''
            self.location_dest_id = self.move_id.location_id or ''

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id:
            if self.move_id:
                # employee = self.employee_id
                self.description = self._get_description(self.move_id.move_type_id)

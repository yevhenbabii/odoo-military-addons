from odoo import _, api, fields, models
from odoo.exceptions import UserError


class HrMove(models.Model):
    _name = "hr.move"
    _description = "Staff Move"
    _order = "id name desc"

    name = fields.Char('Reference', default='/',
                       copy=False, index=True, readonly=True)
    origin = fields.Char(
        'Source Document', index=True,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        help="Reference of the document")
    note = fields.Text('Notes')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', compute='_compute_state',
        copy=False, index=True, readonly=True, store=True, tracking=True)
    date = fields.Datetime(
        'Creation Date',
        default=fields.Datetime.now, 
        index=True, 
        tracking=True,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        help="Creation Date, usually the time of the order")
    date_done = fields.Datetime('Date of Transfer', 
                                copy=False, 
                                readonly=True,
                                help="Date at which the transfer has been processed or cancelled.")
    location_id = fields.Many2one(
        'generic.location', 
        "Source Location",
        default=lambda self: self.env['hr.move.type'].browse(
            self._context.get('default_move_type_id')).default_location_src_id,
        check_company=True,
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]})
    location_dest_id = fields.Many2one(
        'generic.location', "Destination Location",
        default=lambda self: self.env['hr.move.type'].browse(
            self._context.get('default_move_type_id')).default_location_dest_id,
        check_company=True,
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]})
    move_line_ids = fields.One2many('hr.move.line',
                                    'move_id',
                                    'Operations',
                                    copy=True)
    move_type_id = fields.Many2one(
        'hr.move.type',
        'Operation Type',
        required=True, readonly=True,
        states={'draft': [('readonly', False)]})
    move_type_code = fields.Selection(
        related='move_type_id.code',
        readonly=True)
    partner_id = fields.Many2one(
        'res.partner',
        'Partner',
        check_company=True,
        states={'done': [('readonly', True)],
                'cancel': [('readonly', True)]})
    company_id = fields.Many2one(
        'res.company', string='Company', related='move_type_id.company_id',
        readonly=True, store=True, index=True)
    user_id = fields.Many2one(
        'res.users', 'Responsible', tracking=True,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        default=lambda self: self.env.user)
    owner_id = fields.Many2one(
        'res.partner', 'Assign Owner',
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        check_company=True,
        help="When validating the transfer, the products will be assigned to this owner.")
    employee_id = fields.Many2one('hr.employee',
                                  'Employee',
                                  related='move_line_ids.employee_id',
                                  readonly=True)

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        for move in self:
            move_id = isinstance(move.id, int) and move.id or getattr(move, '_origin',
                                                                               False) and move._origin.id
            if move_id:
                moves = self.env['hr.move.line'].search([('move_id', '=', move_id)])
                for move in moves:
                    move.write({'partner_id': move.partner_id.id})

    @api.model
    def create(self, vals):
        defaults = self.default_get(['name', 'move_type_id'])
        move_type = self.env['hr.move.type'].browse(
            vals.get('move_type_id', defaults.get('move_type_id')))
        if vals.get('name', '/') == '/' and defaults.get('name', '/') == '/' and vals.get(
                'move_type_id', defaults.get('move_type_id')):
            if move_type.sequence_id:
                vals['name'] = move_type.sequence_id.next_by_id()
        moves = vals.get('move_lines', [])
        if moves and ((vals.get('location_id') and vals.get('location_dest_id')) or vals.get(
                'partner_id')):
            for move in moves:
                if len(move) == 3 and move[0] == 0:
                    if vals.get('location_id') and vals.get('location_dest_id'):
                        move[2]['location_id'] = vals['location_id']
                        move[2]['location_dest_id'] = vals['location_dest_id']
                        move_type = self.env['hr.move.type'].browse(
                            vals['move_type_id'])
                        if 'move_type_id' not in move[2] or move[2]['move_type_id'] != move_type.id:
                            move[2]['move_type_id'] = move_type.id
                            move[2]['company_id'] = move_type.company_id.id
                    if vals.get('partner_id'):
                        move[2]['partner_id'] = vals.get('partner_id')
        res = super(HrMove, self).create(vals)
        res._autoconfirm_move()
        if vals.get('move_type_id'):
            for move in res.move_lines:
                if not move.description_move:
                    move.description_move = move.employee_id.with_context(
                        lang=move._get_lang())._get_description(move.move_id.move_type_id)
        return res

    def write(self, vals):
        if vals.get('move_type_id') and any(move.state != 'draft' for move in self):
            raise UserError(
                _("Changing the operation type of this record is forbidden at this point."))
        # set partner as a follower and unfollow old partner
        res = super(HrMove, self).write(vals)
        after_vals = {}
        if vals.get('location_id'):
            after_vals['location_id'] = vals['location_id']
        if vals.get('location_dest_id'):
            after_vals['location_dest_id'] = vals['location_dest_id']
        if 'partner_id' in vals:
            after_vals['partner_id'] = vals['partner_id']
        if vals.get('move_lines'):
            self.action_confirm()
        return res

    def action_confirm(self):
        self._check_company()
        self.mapped('move_lines').filtered(lambda move: move.state == 'draft')._action_confirm()
        return True

    def unlink(self):
        self.mapped('move_lines')._action_cancel()
        self.with_context(prefetch_fields=False).mapped(
            'move_lines').unlink()  # Checks if moves are not done
        return super(HrMove, self).unlink()

    def action_assign_partner(self):
        for move in self:
            move.move_lines.write({'partner_id': move.partner_id.id})

    def action_cancel(self):
        self.mapped('move_lines')._action_cancel()
        self.write({'is_locked': True})
        self.filtered(lambda x: not x.move_lines).state = 'cancel'
        return True

    def _action_done(self):
        self._check_company()

        todo_moves = self.mapped('move_lines').filtered(
            lambda self: self.state in ['draft', 'confirmed'])
        for move in self:
            if move.owner_id:
                move.move_lines.write({'restrict_partner_id': move.owner_id.id})
                move.move_line_ids.write({'owner_id': move.owner_id.id})
        todo_moves._action_done(cancel_backorder=self.env.context.get('cancel_backorder'))
        self.write({'date_done': fields.Datetime.now(), 'priority': '0'})

        # if incoming moves make other confirmed/partially_available moves available, assign them
        done_incoming_moves = self.filtered(
            lambda p: p.move_type_id.code == 'incoming').move_lines.filtered(
            lambda m: m.state == 'done')
        done_incoming_moves._trigger_assign()

        return True

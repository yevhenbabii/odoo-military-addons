from odoo import fields, models


class HrInventory(models.Model):
    _name = "hr.inventory"
    _description = "Inventory"
    _order = "date desc"

    name = fields.Char(
        'Inventory Reference',
        default="Inventory",
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]}
    )
    date = fields.Datetime(
        'Inventory Date',
        readonly=True,
        required=True,
        default=fields.Datetime.now,
    )
    line_ids = fields.One2many(
        'hr.inventory.line',
        'inventory_id',
        string='Inventories',
        copy=False, readonly=False,
        states={'done': [('readonly', True)]}
    )
    move_ids = fields.One2many(
        'hr.move',
        'inventory_id',
        string='Created Moves',
        states={'done': [('readonly', True)]}
    )
    state = fields.Selection(
        string='Status',
        selection=[
            ('draft', 'Draft'),
            ('cancel', 'Cancelled'),
            ('confirm', 'In Progress'),
            ('done', 'Validated'),
        ],
        copy=False,
        index=True,
        readonly=True,
        tracking=True,
        default='draft'
    )
    company_id = fields.Many2one(
        'res.company',
        'Company',
        readonly=True,
        index=True,
        required=True,
        states={'draft': [('readonly', False)]},
        default=lambda self: self.env.company
    )
    location_ids = fields.Many2many(
        'hr.work.location', string='Locations',
        readonly=True, check_company=True,
        states={'draft': [('readonly', False)]},
        # domain="[('company_id', '=', company_id), ('usage', 'in', ['internal', 'transit'])]"
    )
    employee_ids = fields.Many2many(
        'hr.inventory.line',
        'employee_id',
        string='Employees',
        check_company=True,
        domain="[('type', '=', 'employee'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        readonly=True,
        states={'draft': [('readonly', False)]},
        help="Specify Employees to focus your inventory on particular Employees.")


class HrInventoryLine(models.Model):
    _name = "hr.inventory.line"
    _description = "Employee Inventory Line"
    _order = "employee_id, inventory_id, location_id, prod_lot_id"

    is_editable = fields.Boolean(help="Technical field to restrict editing.")
    inventory_id = fields.Many2one(
        'hr.inventory',
        'Inventory',
        check_company=True,
        index=True,
        ondelete='cascade')
    partner_id = fields.Many2one('res.partner', 'Owner', check_company=True)
    employee_id = fields.Many2one(
        'hr.employee',
        'Employee',
        check_company=True,
        domain=lambda self: self._domain_employee_id(),
        index=True, required=True)
    department_id = fields.Many2one(
        related='employee_id.department_id',
        store=True)
    location_id = fields.Many2one(
        'hr.work.location',
        'Location',
        check_company=True,
        domain=lambda self: self._domain_location_id(),
        index=True, required=True)
    company_id = fields.Many2one(
        'res.company', 'Company', related='inventory_id.company_id',
        index=True, readonly=True, store=True)
    state = fields.Selection(string='Status',
                             related='inventory_id.state')
    inventory_date = fields.Datetime('Inventory Date',
                                     readonly=True,
                                     default=fields.Datetime.now,
                                     help="Last date at which the On Hand Quantity has been computed.")
    outdated = fields.Boolean(string='Quantity outdated',
                              compute='_compute_outdated', search='_search_outdated')

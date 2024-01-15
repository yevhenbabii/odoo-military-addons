from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError


# ToDo:
# Add job verification procedures:
#     - job should be available for assignment (filter)
#     - verify on assignment that job expected employee is not < 0


class HrTransfer(models.Model):
    _name = "hr.transfer"
    _inherit = ["mail.thread"]
    _description = "Employee Transfer"
    _rec_name = "complete_name"
    _check_company_auto = True
    _order = "date desc"

    number = fields.Char("Order Number",
                         required=True,
                         readonly=True,
                         states={'draft': [('readonly', False)]})
    complete_name = fields.Char("Complete Name",
                                compute="_compute_complete_name",
                                store=True,
                                tracking=True,
                                default="Noname")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('cancel', 'Cancelled'),
        ('confirm', 'Confirmed'),
        ('done', 'Done'),
    ],
        string='Status',
        readonly=True,
        copy=False,
        index=True,
        default='draft',
        tracking=3)
    date = fields.Date(string='Date',
                       required=True,
                       readonly=True,
                       index=True,
                       states={'draft': [('readonly', False)]},
                       copy=False,
                       default=fields.Date.today,
                       help="Date of transfer")
    partner_id = fields.Many2one(
        'res.partner',
        string='Order Author',
        readonly=True,
        states={'draft': [('readonly', False)]},
        required=True,
        change_default=True,
        index=True,
        tracking=1,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        default=lambda self: self.env.company.partner_id)
    transfer_line = fields.One2many('hr.transfer.line', 'transfer_id',
                                    string='Transfer Lines',
                                    states={'done': [('readonly', True)],
                                            'confirm': [('readonly', True)]},
                                    copy=True, auto_join=True)
    description = fields.Text('Description')
    company_id = fields.Many2one('res.company',
                                 'Company',
                                 required=True,
                                 index=True,
                                 default=lambda self: self.env.company)

    @api.depends("number", "partner_id", "date")
    def _compute_complete_name(self):
        for rec in self:
            number = rec.number if rec.number else ''
            partner = rec.partner_id.name if rec.partner_id else ''
            date = rec.date.strftime("%d.%m.%Y") if rec.date else ''
            rec.complete_name = "Order from %s # %s %s" % (date, number, partner)

    def effective_date_in_past(self):
        for transfer in self:
            if transfer.date > fields.Date.today():
                raise UserError(
                    _(
                        "Transfer date should be before today!"
                    )
                )
        return True

    def unlink(self):

        if not self.env.context.get("force_delete", False):
            for transfer in self:
                if transfer.state not in ["draft", "cancel"]:
                    raise UserError(
                        _(
                            "Unable to Delete Transfer!\n"
                            "Transfer has been initiated. Either cancel the transfer or\n"
                            "create another transfer to undo it."
                        )
                    )
        return super(HrTransfer, self).unlink()

    def action_done(self):
        self.ensure_one()
        has_permission = self._check_permission_group("military_job.group_hr_transfer")
        if has_permission and self.effective_date_in_past():
            self.state_done()
        else:
            self.write({"state": "done"})

    def action_confirm(self):
        self.ensure_one()
        has_permission = self._check_permission_group("military_job.group_hr_transfer")
        if has_permission:
            self.state_confirm()

    def action_cancel(self):
        self.ensure_one()
        has_permission = self._check_permission_group(
            "military_job.group_hr_transfer"
        )
        if has_permission:
            self.write({"state": "cancel"})

    def action_draft(self):
        self.ensure_one()
        has_permission = self._check_permission_group(
            "military_job.group_hr_transfer"
        )
        if has_permission:
            self.write({"state": "draft"})

    def _check_permission_group(self, group=None):

        for transfer in self:
            if group and not transfer.user_has_groups(group):
                raise AccessError(
                    _("You don't have the access rights to take this action.")
                )
            else:
                continue
        return True

    def state_confirm(self):
        for transfer in self:
            transfer.state = "confirm"
        return True

    def state_done(self):
        today = fields.Date.today()
        for transfer in self:
            if transfer.date <= today:
                for transfer_line in transfer.transfer_line:
                    transfer_line.employee_id.job_id = transfer_line.dst_job_id
                transfer.state = "done"
            else:
                raise UserError(
                    _(
                        "Transfer date should be before today!"
                    )
                )
        return True

    def signal_confirm(self):
        for transfer in self:
            if (
                    self.user_has_groups("military_job.group_hr_transfer")
                    and transfer.effective_date_in_past()
            ):
                transfer.state = "confirm"
            else:
                transfer.state_confirm()
        return True


class HrTransferLine(models.Model):
    _name = "hr.transfer.line"
    _description = "Employee Transfer Line"
    _rec_name = "date"
    _check_company_auto = True

    transfer_id = fields.Many2one('hr.transfer',
                                  string='Transfer Reference',
                                  required=True,
                                  ondelete='cascade',
                                  index=True, copy=False)
    transfer_partner_id = fields.Many2one(related='transfer_id.partner_id',
                                          store=True,
                                          string='Customer',
                                          readonly=False)
    state = fields.Selection(
        related='transfer_id.state',
        string='Transfer Status',
        readonly=True,
        copy=False,
        store=True,
    )
    # TODO add temporary job option
    temp = fields.Boolean("Temporary Job", default=False)
    employee_id = fields.Many2one(
        string="Employee",
        comodel_name="hr.employee",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        check_company=True,
        # domain="[('id', 'not in', transfer_line.mapped('employee_id').ids)]",
        # domain=lambda self: self._get_employee_domain(),
        # domain=[('forum_id', 'in', self.mapped.ids)],
        # domain=lambda self: [('id', 'not in', self.forum_id.ids)],

        # domain=lambda self: [('id', 'not in', self.mapped('employee_id').ids)],
    )
    description = fields.Text(string='Description')
    src_job_id = fields.Many2one(
        string="From Job",
        comodel_name="hr.job",
        compute="_compute_onchange_employee",
        store=True,
        readonly=True,
        check_company=True,
    )
    src_department_id = fields.Many2one(
        string="From Department",
        compute="_compute_onchange_employee",
        comodel_name="hr.department",
        store=True,
        readonly=True,
    )
    dst_job_id = fields.Many2one(
        string="Destination Job",
        comodel_name="hr.job",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        check_company=True,
        domain="[('expected_employees', '>', 0)]",
    )
    dst_department_id = fields.Many2one(
        string="Destination Department",
        related="dst_job_id.department_id",
        comodel_name="hr.department",
        store=True,
        readonly=True,
        check_company=True,
    )
    date = fields.Date(
        string="Effective Date",
        related="transfer_id.date",
        required=True,
        readonly=True
    )
    company_id = fields.Many2one(
        string="Company",
        comodel_name="res.company",
        default=lambda self: self.env.company,
        store=True,
        readonly=True,
    )

    @api.depends("employee_id")
    def _compute_onchange_employee(self):
        for transfer in self:
            if transfer.employee_id:
                transfer.src_job_id = transfer.employee_id.job_id
                transfer.src_department_id = transfer.employee_id.department_id
            else:
                transfer.src_job_id = False
                transfer.src_department_id = False

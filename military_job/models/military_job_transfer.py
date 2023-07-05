from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError


class HrTransfer(models.Model):
    _name = "hr.transfer"
    _inherit = ["mail.thread"]
    _description = "Employee Transfer"
    _rec_name = "date"
    _check_company_auto = True
    _order = "date desc"

    number = fields.Char("Order Number", required=True, readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([
        ('draft', 'Draft'),
        ('cancel', 'Cancelled'),
        ('confirm', 'Confirmed'),
        ('done', 'Done'),
    ],
        string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')
    date = fields.Date(string='Date',
                       required=True,
                       readonly=True,
                       index=True,
                       states={'draft': [('readonly', False)]},
                       copy=False, default=fields.Date.today,
                       help="Date of transfer")
    partner_id = fields.Many2one(
        'res.partner', string='Order Author', readonly=True,
        states={'draft': [('readonly', False)]},
        required=True, change_default=True, index=True, tracking=1,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    transfer_line = fields.One2many('hr.transfer.line', 'transfer_id',
                                    string='Transfer Lines',
                                    states={'done': [('readonly', True)], 'confirm': [('readonly', True)]},
                                    copy=True, auto_join=True)
    description = fields.Text('Description')
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)

    def effective_date_in_future(self):

        for transfer in self:
            if transfer.date <= fields.Date.today():
                return False
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

    def action_transfer(self):

        self.ensure_one()
        has_permission = self._check_permission_group(
            "military_job.group_hr_transfer"
        )
        if has_permission and not self.effective_date_in_future():
            self.state_done()
        else:
            self.write({"state": "pending"})

    def action_confirm(self):

        self.ensure_one()
        has_permission = self._check_permission_group(
            "military_job.group_hr_transfer"
        )
        if has_permission:
            self.signal_confirm()

    def action_cancel(self):

        self.ensure_one()
        has_permission = self._check_permission_group(
            "military_job.group_hr_transfer"
        )
        if has_permission:
            self.write({"state": "cancel"})

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
            # self._check_state(transfer.date)
            transfer.state = "confirm"

        return True

    def state_done(self):

        today = fields.Date.today()

        for transfer in self:
            if transfer.date <= today:
                transfer.transfer_line.employee_id.job_id = transfer.transfer_line.dst_id
                transfer.state = "done"
            else:
                return False

        return True

    def signal_confirm(self):

        for transfer in self:
            # self._check_state(transfer.date)
            # If the user is a member of 'approval' group, go straight to 'approval'
            if (
                    self.user_has_groups("military_job.group_hr_transfer")
                    and transfer.effective_date_in_future()
            ):
                transfer.state = "pending"
            else:
                transfer.state_confirm()

        return True


class HrTransferLine(models.Model):
    _name = "hr.transfer.line"
    # _inherit = ["mail.thread"]
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
        related='transfer_id.state', string='Transfer Status', readonly=True, copy=False, store=True,
        default='draft')
    # TODO add temporary job option
    # temp = fields.Boolean("Temporary Job", default=False)
    employee_id = fields.Many2one(
        string="Employee",
        comodel_name="hr.employee",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        check_company=True,
    )
    description = fields.Text(string='Description')
    src_job = fields.Char(
        string="From Job",
        # comodel_name="hr.job",
        # related="employee_id.job_id",
        compute="_compute_onchange_employee",
        store=True,
        readonly=True,
        # states={"draft": [("readonly", False)]},
        # check_company=True,
    )
    src_department = fields.Char(
        string="From Department",
        compute="_compute_onchange_employee",
        # related="src_id.department_id",
        # comodel_name="hr.department",
        store=True,
        readonly=True,
    )
    dst_id = fields.Many2one(
        string="Destination Job",
        comodel_name="hr.job",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        check_company=True,
    )
    dst_department_id = fields.Many2one(
        string="Destination Department",
        related="dst_id.department_id",
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
                transfer.src_job = transfer.employee_id.job_id.display_name
                transfer.src_department = transfer.employee_id.department_id.display_name
            else:
                transfer.src_job = False
                transfer.src_department = False

    def _track_subtype(self, init_values):
        self.ensure_one()
        if "state" in init_values:
            if self.state == "confirm":
                return self.env.ref("hr_transfer_line.mt_alert_xfer_confirmed")
            elif self.state == "pending":
                return self.env.ref("hr_transfer_line.mt_alert_xfer_pending")
            elif self.state == "done":
                return self.env.ref("hr_transfer_line.mt_alert_xfer_done")
        return super(HrTransferLine, self)._track_subtype(init_values)

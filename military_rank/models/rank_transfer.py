# Copyright (C) 2021 Trevi Software (https://trevi.et)
# Copyright (C) 2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError


# TODO make transfer line
class RankTransfer(models.Model):
    _name = "rank.transfer"
    _inherit = ["mail.thread"]
    _description = "Rank Transfer"
    _rec_name = "date"
    _check_company_auto = True

    number = fields.Char("Order Number")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('cancel', 'Cancelled')],
        string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')
    date = fields.Datetime(string='Date', required=True, readonly=True, index=True,
                           states={'draft': [('readonly', False)]},
                           copy=False, default=fields.Datetime.now,
                           help="Date of transfer")
    partner_id = fields.Many2one(
        'res.partner', string='Order Author', readonly=True,
        states={'draft': [('readonly', False)]},
        required=True, change_default=True, index=True, tracking=1,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    transfer_line = fields.One2many('rank.transfer.line', 'transfer_id',
                                    string='Transfer Lines',
                                    states={'cancel': [('readonly', True)],
                                            'confirm': [('readonly', True)]},
                                    copy=True, auto_join=True)
    description = fields.Text('Description')


class RankTransferLine(models.Model):
    _name = "rank.transfer.line"
    _inherit = ["mail.thread"]
    _description = "Rank Transfer Line"
    _rec_name = "date"
    _check_company_auto = True

    transfer_id = fields.Many2one('rank.transfer',
                                  string='Transfer Reference',
                                  required=True,
                                  ondelete='cascade',
                                  index=True, copy=False)
    transfer_partner_id = fields.Many2one(related='transfer_id.partner_id',
                                          store=True,
                                          string='Customer',
                                          readonly=False)
    date = fields.Date(
        string="Effective Date",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("confirm", "Confirmed"),
            ("pending", "Pending"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
        ],
        default="draft",
        readonly=True,
    )
    company_id = fields.Many2one(
        string="Company",
        comodel_name="res.company",
        default=lambda self: self.env.company,
        store=True,
        readonly=True,
    )
    employee_id = fields.Many2one(
        string="Employee",
        comodel_name="hr.employee",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        check_company=True,
    )
    src_id = fields.Many2one(
        string="From",
        comodel_name="military.rank",
        compute="_compute_onchange_employee",
        store=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    dst_id = fields.Many2one(
        string="Destination",
        comodel_name="military.rank",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )

    @api.depends("employee_id")
    def _compute_onchange_employee(self):
        for transfer in self:
            if transfer.employee_id:
                transfer.src_id = transfer.employee_id.rank_id
            else:
                transfer.src_id = False

    def effective_date_in_future(self):

        for transfer in self:
            if transfer.date <= fields.Date.today():
                return False
        return True

    def unlink(self):

        if not self.env.context.get("force_delete", False):
            for transfer in self:
                if transfer.state not in ["draft"]:
                    raise UserError(
                        _(
                            "Unable to Delete Transfer!\n"
                            "Transfer has been initiated. Either cancel the transfer or\n"
                            "create another transfer to undo it."
                        )
                    )
        return super(RankTransferLine, self).unlink()

    def action_transfer(self):

        self.ensure_one()
        has_permission = self._check_permission_group(
            "military_rank.group_rank_transfer"
        )
        if has_permission and not self.effective_date_in_future():
            self.state_done()
        else:
            self.write({"state": "pending"})

    def action_confirm(self):

        self.ensure_one()
        has_permission = self._check_permission_group(
            "military_rank.group_rank_transfer"
        )
        if has_permission:
            self.signal_confirm()

    def action_cancel(self):

        self.ensure_one()
        has_permission = self._check_permission_group(
            "military_rank.group_rank_transfer"
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
            transfer.state = "confirm"
        return True

    def state_done(self):
        today = fields.Date.today()
        for transfer in self:
            if transfer.date <= today:
                transfer.employee_id.rank_id = transfer.dst_id
                transfer.state = "done"
            else:
                return False
        return True

    def signal_confirm(self):

        for transfer in self:
            # If the user is a member of 'approval' group, go straight to 'approval'
            if (
                    self.user_has_groups("military_rank.group_rank_transfer")
                    and transfer.effective_date_in_future()
            ):
                transfer.state = "pending"
            else:
                transfer.state_confirm()

        return True

    @api.model
    def try_pending_transfers(self):
        """Completes pending transfers. Called from the scheduler."""

        self._check_permission_group("military_rank.group_rank_transfer")

        Transfer = self.env["military.rank"]
        pending_transfers = Transfer.search(
            [("state", "=", "pending"), ("date", "<=", fields.Date.today())]
        )

        for transfer in pending_transfers:
            transfer.state_done()

        return True

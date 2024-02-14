from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class HrWorkLocation(models.Model):
    _inherit = 'hr.work.location'
    _description = 'Work Location'
    _parent_store = True
    _rec_name = 'complete_name'

    parent_id = fields.Many2one(
        'hr.work.location',
        'Parent Location',
        index=True,
    )
    child_ids = fields.One2many(
        'hr.work.location',
        'parent_id',
        string='Sublocations'
    )
    parent_path = fields.Char(
        index=True,
        unaccent=False
    )
    complete_name = fields.Char(
        'Complete Name',
        compute='_compute_complete_name',
        recursive=True,
        store=True
    )
    address_id = fields.Many2one(
        'res.partner',
        required=False,
        string="Work Address",
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]"
    )

    @api.constrains('parent_id')
    def _check_parent_id(self):
        if not self._check_recursion():
            raise ValidationError(_('You cannot create recursive locations.'))

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for location in self:
            if location.parent_id:
                location.complete_name = '%s / %s' % (
                location.parent_id.complete_name, location.name)
            else:
                location.complete_name = location.name

from odoo import api, models


class HrEmployee(models.AbstractModel):
    _name = 'report.military_employee.form5'

    @api.model
    def get_report_values(self, docids, data=None):
        # Логіка для збору даних
        records = self.env['hr.employee'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'hr.employee',
            'docs': records,
            'data': data,
        }

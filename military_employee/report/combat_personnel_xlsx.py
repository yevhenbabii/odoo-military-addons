from odoo import models


class CombatPersonnelXlsx(models.AbstractModel):
    _name = 'military_employee.combat_personnel_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = "Project Xlsx report"

    def generate_xlsx_report(self, workbook, data, sale):
        for obj in sale:
            sheet = workbook.add_worksheet(obj.name)
            bold = workbook.add_format({'bold': True})
            date_format = workbook.add_format({'num_format': 'dd.mm.yyyy'})
            align_center = workbook.add_format({'align': 'center'})
            align_center_b = workbook.add_format({'align': 'center', 'bold': True})
            row = 5
            col = 5
            sheet.write(row, col, 'Project Manager', bold)
            col += 1
            sheet.write(row, col, obj.user_id.name)
            row += 1
            col -= 1
            sheet.write(row, col, 'Start Date', bold)
            col += 1
            sheet.write(row, col, obj.date_start, date_format)
            row += 1
            col -= 1
            sheet.write(row, col, 'End Date', bold)
            col += 1
            sheet.write(row, col, obj.date, date_format)
            row = 1
            col = 1
            sheet.merge_range(row, col, row, col + 5, 'Project', align_center_b)
            row += 2
            col = 1
            sheet.write(row, col, obj.name, bold)
            row += 2
            sheet.write(row, col, 'Customer', bold)
            col += 1
            sheet.write(row, col, obj.partner_id.name)
            row += 1
            col -= 1
            sheet.write(row, col, 'Tags', bold)
            col += 1
            tag_list = []
            for tg in obj.tag_ids:
                tag_list.append(tg.name)
            sheet.write(row, col, ', '.join(tag_list))
            tag_list.clear()
            row += 1
            col -= 1
            sheet.write(row, col, 'Company', bold)
            col += 1
            sheet.write(row, col, obj.company_id.name)
            if obj.description:
                row += 2
                col = 1
                sheet.merge_range(row, col, row, col + 5, 'Description', align_center)
                row += 1
                col = 1
                sheet.merge_range(row, col, row, col + 5, obj.description)
            if obj.tasks:
                row += 2
                col = 1
                sheet.merge_range(row, col, row, col + 5, 'Tasks', align_center)
                row += 1
                col = 1
                sheet.write(row, col, 'Name', bold)
                col += 1
                sheet.write(row, col, 'Assignees', bold)
                col += 1
                sheet.write(row, col, 'Parent Task', bold)
                col += 1
                sheet.write(row, col, 'Customer', bold)
                col += 1
                sheet.write(row, col, 'Tags', bold)
                col += 1
                sheet.write(row, col, 'Deadline', bold)
                row += 1
                col = 1
                for record in obj.tasks:
                    sheet.write(row, col, record.name)
                    col += 1
                    usr_list = []
                    for usr in record.user_ids:
                        usr_list.append(usr.name)
                    sheet.write(row, col, ', '.join(usr_list))
                    usr_list.clear()
                    col += 1
                    sheet.write(row, col, record.parent_id.name)
                    col += 1
                    sheet.write(row, col, record.partner_id.name)
                    col += 1
                    tag_list = []
                    for usr in record.tag_ids:
                        tag_list.append(usr.name)
                    sheet.write(row, col, ', '.join(tag_list))
                    tag_list.clear()
                    col += 1
                    sheet.write(row, col, record.date_deadline, date_format)
                    col = 1
                    row += 1
        workbook.close()

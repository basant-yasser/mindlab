
from odoo import api, fields, models


class OpAttendanceLine(models.Model):
    _inherit = "op.attendance.line"

    present = fields.Boolean('Present', tracking=True,default=True)
    program_details_id = fields.Many2one('program.details', string='Kit Type')
    kit_level_id = fields.Many2one(related='program_details_id.kit_level_id', string='Kit Level')
    project_program_ids = fields.Many2many(related='program_details_id.project_program_ids', string='Project Program')






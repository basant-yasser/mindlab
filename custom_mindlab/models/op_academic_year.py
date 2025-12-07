from odoo import models, fields, api


class OpAcademicYear(models.Model):
    _inherit = 'op.academic.year'

    op_student_id = fields.Many2one('op.student',string='Op Student')


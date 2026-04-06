from odoo import fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    mindlab_student_id = fields.Many2one('mindlab.student', string='Mindlab Student', index=True)
    mindlab_enrollment_id = fields.Many2one('mindlab.enrollment', string='Mindlab Enrollment', index=True)

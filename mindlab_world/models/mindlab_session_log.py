from odoo import fields, models


class MindlabSessionLog(models.Model):
    _name = 'mindlab.session.log'
    _description = 'Mindlab Session Balance Log'
    _order = 'date desc, id desc'

    enrollment_id = fields.Many2one('mindlab.enrollment', required=True, ondelete='cascade')
    student_id = fields.Many2one('mindlab.student', required=True)
    attendance_id = fields.Many2one('mindlab.attendance', ondelete='set null')
    action_type = fields.Selection([
        ('consume', 'Consume'),
        ('restore', 'Restore'),
        ('manual_adjustment', 'Manual Adjustment'),
    ], required=True)
    qty = fields.Float(required=True, default=1.0)
    date = fields.Datetime(default=fields.Datetime.now, required=True)
    reason = fields.Char()
    before_remaining = fields.Float()
    after_remaining = fields.Float()
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user, required=True)

    _mindlab_session_log_qty_positive = models.Constraint(
        'CHECK(qty >= 0)',
        'Quantity must be non-negative.'
    )

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    mindlab_auto_invoice_on_enrollment = fields.Boolean(config_parameter='mindlab_world.auto_invoice_on_enrollment')
    mindlab_default_attendance_deduction_mode = fields.Selection([
        ('present_only', 'Present Only'),
        ('present_absent', 'Present + Absent'),
        ('present_absent_excused', 'Present + Absent + Excused'),
    ], default='present_only', config_parameter='mindlab_world.default_attendance_deduction_mode')
    mindlab_deduct_present = fields.Boolean(default=True, config_parameter='mindlab_world.deduct_present')
    mindlab_deduct_absent = fields.Boolean(default=False, config_parameter='mindlab_world.deduct_absent')
    mindlab_deduct_excused = fields.Boolean(default=False, config_parameter='mindlab_world.deduct_excused')
    mindlab_warn_low_sessions = fields.Boolean(default=True, config_parameter='mindlab_world.warn_low_sessions')
    mindlab_low_session_threshold = fields.Integer(default=2, config_parameter='mindlab_world.low_session_threshold')
    mindlab_enable_progression_tracking = fields.Boolean(default=True, config_parameter='mindlab_world.enable_progression_tracking')
    mindlab_require_evaluation_for_progression = fields.Boolean(default=False, config_parameter='mindlab_world.require_evaluation_for_progression')
    mindlab_enable_student_session_logs = fields.Boolean(default=True, config_parameter='mindlab_world.enable_student_session_logs')

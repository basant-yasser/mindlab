from odoo import fields, models


class MindlabStudentProgression(models.Model):
    _name = 'mindlab.student.progression'
    _description = 'Mindlab Student Progression'
    _order = 'date desc, id desc'

    student_id = fields.Many2one('mindlab.student', required=True, ondelete='cascade')
    from_stage_id = fields.Many2one('mindlab.stage')
    to_stage_id = fields.Many2one('mindlab.stage', required=True)
    date = fields.Date(default=fields.Date.context_today, required=True)
    reason = fields.Char()
    evaluation_id = fields.Many2one('mindlab.student.evaluation', ondelete='set null')
    notes = fields.Text()

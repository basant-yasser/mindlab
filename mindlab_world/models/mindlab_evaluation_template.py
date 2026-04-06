from odoo import fields, models


class MindlabEvaluationTemplate(models.Model):
    _name = 'mindlab.evaluation.template'
    _description = 'Mindlab Evaluation Template'

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    stage_id = fields.Many2one('mindlab.stage')
    offer_id = fields.Many2one('mindlab.offer')
    line_ids = fields.One2many('mindlab.evaluation.template.line', 'template_id')


class MindlabEvaluationTemplateLine(models.Model):
    _name = 'mindlab.evaluation.template.line'
    _description = 'Mindlab Evaluation Template Line'
    _order = 'sequence, id'

    template_id = fields.Many2one('mindlab.evaluation.template', required=True, ondelete='cascade')
    criterion_name = fields.Char(required=True)
    weight = fields.Float(default=1.0)
    max_score = fields.Float(default=100.0)
    category = fields.Char()
    sequence = fields.Integer(default=10)

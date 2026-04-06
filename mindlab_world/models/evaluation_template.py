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
    sequence = fields.Integer(default=10)
    criterion_name = fields.Char(required=True)
    category = fields.Char()
    weight = fields.Float(default=0.0, help='Criterion weight as a percentage.')
    level_1_description = fields.Text(string='1 – Not Yet')
    level_2_description = fields.Text(string='2 – Emerging')
    level_3_description = fields.Text(string='3 – Developing')
    level_4_description = fields.Text(string='4 – Achieved')
    max_score = fields.Integer(default=4)

from odoo import fields, models


class MindlabStage(models.Model):
    _name = 'mindlab.stage'
    _description = 'Mindlab Stage'
    _order = 'sequence, name'

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    description = fields.Text()

    _mindlab_stage_code_unique = models.Constraint(
        'UNIQUE(code)',
        'Stage code must be unique.'
    )

from odoo import fields, models


class MindlabCategory(models.Model):
    _name = 'mindlab.category'
    _description = 'Mindlab Offer Category'
    _order = 'name'

    name = fields.Char(required=True)
    code = fields.Char()
    active = fields.Boolean(default=True)
    description = fields.Text()

    _mindlab_category_name_unique = models.Constraint(
        'UNIQUE(name)',
        'Category name must be unique.'
    )

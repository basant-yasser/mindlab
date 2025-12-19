from odoo import models, fields, api


class KitType(models.Model):
    _name = 'kit.type'
    _rec_name = 'name'

    name = fields.Char('Kit Type', required=True)
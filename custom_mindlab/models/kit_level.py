from odoo import models, fields, api


class Kitlevel(models.Model):
    _name = 'kit.level'
    _rec_name = 'name'

    name = fields.Char(string='Level Name',required=True)
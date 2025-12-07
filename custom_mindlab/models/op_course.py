
from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'op.course'

    number_of_sessions = fields.Integer(string=' Number of Sessions')
    note = fields.Text('Notes')

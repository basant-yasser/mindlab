from odoo import models, fields, api


class ProjectProgram(models.Model):
    _name = 'project.program'
    _rec_name = 'name'

    name = fields.Char(string='Level Name', required=True)
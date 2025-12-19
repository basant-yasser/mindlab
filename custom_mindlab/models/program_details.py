from odoo import models, fields, api


class ProgramDetails(models.Model):
    _name = 'program.details'
    _rec_name = 'kit_type_id'

    kit_type_id = fields.Many2one('kit.type', string='Kit Type')
    kit_level_id = fields.Many2one('kit.level', string='Kit Level')
    project_program_ids = fields.Many2many('project.program', string='Project')

from odoo import api, fields, models
import json


class OpAttendanceLine(models.Model):
    _inherit = "op.attendance.line"



    present = fields.Boolean('Present', tracking=True,default=True)
    program_details_id = fields.Many2one('program.details', string='Kit Type')
    kit_level_id = fields.Many2one('kit.level', string='Kit Level')
    kit_level_domain = fields.Char(compute='_compute_kit_level_domain')


    program_details_domain = fields.Char(compute='_compute_project_program_domain')
    project_program_ids = fields.Many2many('project.program', string='Project Program')

    @api.depends('kit_level_id', 'program_details_id', 'program_details_id.kit_type_id')
    def _compute_project_program_domain(self):
        """Filter project programs based on selected kit level and kit type"""
        for record in self:
            if record.kit_level_id and record.program_details_id and record.program_details_id.kit_type_id:
                # Find program.details with same kit_type AND kit_level
                matching_details = self.env['program.details'].search([
                    ('kit_type_id', '=', record.program_details_id.kit_type_id.id),
                    ('kit_level_id', '=', record.kit_level_id.id)
                ])

                # Get all project programs from matching program.details
                project_programs = matching_details.mapped('project_program_ids').ids

                if project_programs:
                    record.program_details_domain = json.dumps([('id', 'in', project_programs)])
                else:
                    record.program_details_domain= json.dumps([('id', '=', False)])
            else:
                record.program_details_domain = json.dumps([('id', '=', False)])

    @api.depends('program_details_id', 'program_details_id.kit_type_id')
    def _compute_kit_level_domain(self):
        """Show all kit levels for selected kit type"""
        for record in self:
            if record.program_details_id and record.program_details_id.kit_type_id:
                # Find all program.details with the same kit_type
                same_kit_type = self.env['program.details'].search([
                    ('kit_type_id', '=', record.program_details_id.kit_type_id.id)
                ])

                # Get all kit_level_ids
                kit_level_ids = same_kit_type.mapped('kit_level_id').ids

                if kit_level_ids:
                    record.kit_level_domain = json.dumps([('id', 'in', kit_level_ids)])
                else:
                    record.kit_level_domain = json.dumps([('id', '=', False)])
            else:
                record.kit_level_domain = json.dumps([('id', '=', False)])

    @api.onchange('program_details_id')
    def _onchange_program_details_id(self):
        """Reset kit_level and project_programs when kit type changes"""
        # Reset dependent fields
        self.kit_level_id = False
        self.project_program_ids = [(5, 0, 0)]

        # Update domains
        if self.program_details_id and self.program_details_id.kit_type_id:
            same_type = self.env['program.details'].search([
                ('kit_type_id', '=', self.program_details_id.kit_type_id.id)
            ])
            kit_levels = same_type.mapped('kit_level_id').ids

            return {
                'domain': {
                    'kit_level_id': [('id', 'in', kit_levels)] if kit_levels else [('id', '=', False)],
                    'project_program_ids': [('id', '=', False)]
                }
            }
        else:
            return {
                'domain': {
                    'kit_level_id': [('id', '=', False)],
                    'project_program_ids': [('id', '=', False)]
                }
            }

    @api.onchange('kit_level_id')
    def _onchange_kit_level_id(self):
        """Reset project_programs when kit level changes"""
        # Clear existing project programs
        self.project_program_ids = [(5, 0, 0)]

        # Update domain
        if self.kit_level_id and self.program_details_id and self.program_details_id.kit_type_id:
            matching_details = self.env['program.details'].search([
                ('kit_type_id', '=', self.program_details_id.kit_type_id.id),
                ('kit_level_id', '=', self.kit_level_id.id)
            ])
            project_programs = matching_details.mapped('project_program_ids').ids

            return {
                'domain': {
                    'project_program_ids': [('id', 'in', project_programs)] if project_programs else [
                        ('id', '=', False)]
                }
            }
        else:
            return {
                'domain': {
                    'project_program_ids': [('id', '=', False)]
                }
            }














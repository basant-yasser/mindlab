from odoo import models, fields, api


class ProgramDetails(models.Model):
    _name = 'program.details'
    _rec_name = 'display_name'

    kit_type_id = fields.Many2one('kit.type', string='Kit Type')
    kit_level_id = fields.Many2one('kit.level', string='Kit Level')
    project_program_ids = fields.Many2many('project.program', string='Project')
    display_name = fields.Char(compute='_compute_display_name')

    @api.depends('kit_type_id', 'kit_level_id')
    def _compute_display_name(self):
        for record in self:
            if record.kit_type_id:
                name = record.kit_type_id.name
                # if record.kit_level_id:
                #     name += f" - {record.kit_level_id.name}"
                record.display_name = name
            else:
                record.display_name = 'Undefined'

    def name_get(self):
        """Display kit type name"""
        result = []
        for record in self:
            name = record.kit_type_id.name if record.kit_type_id else 'No Kit Type'
            result.append((record.id, name))
        return result

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """Show unique kit types only"""
        args = args or []
        domain = args.copy()

        if name:
            domain += [('kit_type_id.name', operator, name)]

        records = self.search(domain, limit=limit)

        # Filter unique kit types
        seen = set()
        unique = self.browse()

        for rec in records:
            if rec.kit_type_id and rec.kit_type_id.id not in seen:
                seen.add(rec.kit_type_id.id)
                unique |= rec

        return unique.name_get()








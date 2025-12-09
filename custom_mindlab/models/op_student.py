from odoo import models, fields, api


class OpStudent(models.Model):
    _inherit = 'op.student'

    whatsapp_number = fields.Char(string='Whatsapp Number')
    registration_source = fields.Selection(
        [('telephone', 'Telephone'), ('whatsapp', 'Whatsapp'),
         ('facebook', 'Facebook'), ('visit', 'Visit'), ('instagram', 'Instagram')],
        'Registration Source', default='telephone')

    academic_year_ids = fields.One2many('op.academic.year','op_student_id',string='Academic Year')
    op_course_id = fields.Many2one('op.course',string='Course')
    number_of_sessions = fields.Integer(related='op_course_id.number_of_sessions',string='Number of Sessions')
    state = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('withdrawn', 'Withdrawn'),
        ('graduated', 'Graduated'),
    ], string='Status',default='')

    relationship_id = fields.Many2one(related='parent_ids.relationship_id', string="Relationship")

    def action_view_student_applications(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "openeducat_admission.act_open_op_admission_view"
        )
        action['domain'] = [
            ('student_id', '=', self.id),
        ]

        return action
    # op_admin_register_id = fields.Many2one('op.admission.register', string="Admission Register")

    # parent_id = fields.Many2one('op.parent', string="Parent")
    #
    # def get_parent(self):
    #     self.ensure_one()
    #     parent = self.env['op.parent'].search([('student_ids', 'in', self.ids)], limit=1)
    #
    #     self.parent_id = parent.id if parent else False
    #
    #     return True


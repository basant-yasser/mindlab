from odoo import api, fields, models
from odoo.exceptions import UserError


class AttendanceBatchAddStudentsWizard(models.TransientModel):
    _name = 'mindlab.attendance.batch.add.students.wizard'
    _description = 'Add Students to Attendance Batch'

    batch_id = fields.Many2one('mindlab.attendance.batch', required=True, readonly=True)
    offer_id = fields.Many2one('mindlab.offer', string='Program', required=True)
    select_all = fields.Boolean(string='Select all program students', default=True)
    enrollment_ids = fields.Many2many(
        'mindlab.enrollment',
        relation='mindlab_att_batch_add_stu_enroll_rel',
        column1='wizard_id',
        column2='enrollment_id',
        string='Students',
        domain="[('offer_id', '=', offer_id), ('state', 'in', ['draft', 'active', 'suspended'])]",
    )

    @api.model
    def default_get(self, fields_list):
        values = super().default_get(fields_list)
        batch = self.env['mindlab.attendance.batch'].browse(self.env.context.get('active_id'))
        if batch:
            values.setdefault('batch_id', batch.id)
            values.setdefault('offer_id', batch.offer_id.id)
        return values

    def action_add_students(self):
        self.ensure_one()
        if not self.batch_id:
            raise UserError('No attendance batch selected.')

        if self.offer_id != self.batch_id.offer_id:
            self.batch_id.offer_id = self.offer_id
            self.batch_id.teacher_id = self.offer_id.teacher_id

        enrollments = self.enrollment_ids
        if self.select_all:
            enrollments = self.env['mindlab.enrollment'].search([
                ('offer_id', '=', self.offer_id.id),
                ('state', 'in', ['draft', 'active', 'suspended']),
            ])

        if not enrollments:
            raise UserError('Please select at least one student enrollment.')

        existing = self.batch_id.line_ids.mapped('enrollment_id')
        to_add = enrollments - existing

        commands = [(0, 0, {'enrollment_id': enrollment.id}) for enrollment in to_add]
        if commands:
            self.batch_id.write({'line_ids': commands})

        return {'type': 'ir.actions.act_window_close'}

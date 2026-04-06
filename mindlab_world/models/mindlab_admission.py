from odoo import api, fields, models
from odoo.exceptions import UserError


class MindlabAdmission(models.Model):
    _name = 'mindlab.admission'
    _description = 'Mindlab Admission'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(default='New', readonly=True, copy=False)
    student_name = fields.Char(required=True, tracking=True)
    student_id = fields.Many2one('mindlab.student', readonly=True, copy=False)
    application_date = fields.Date(default=fields.Date.context_today, required=True)
    parent_id = fields.Many2one('res.partner', string='Parent / Guardian')
    guardian_name = fields.Char()
    mobile = fields.Char()
    email = fields.Char()
    address = fields.Text()
    birth_date = fields.Date()
    desired_offer_id = fields.Many2one('mindlab.offer', string='Desired Program/Course')
    desired_stage_id = fields.Many2one('mindlab.stage')
    notes = fields.Text()
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('enrolled', 'Enrolled'),
    ], default='draft', tracking=True)
    enrollment_ids = fields.One2many('mindlab.enrollment', 'admission_id')
    enrollment_count = fields.Integer(compute='_compute_enrollment_count')

    @api.depends('enrollment_ids')
    def _compute_enrollment_count(self):
        for rec in self:
            rec.enrollment_count = len(rec.enrollment_ids)

    @api.model_create_multi
    def create(self, vals_list):
        seq = self.env['ir.sequence']
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = seq.next_by_code('mindlab.admission') or 'New'
        return super().create(vals_list)

    def action_submit(self):
        self.write({'state': 'submitted'})

    def action_review(self):
        self.write({'state': 'under_review'})

    def action_approve(self):
        self.write({'state': 'approved'})

    def action_reject(self):
        self.write({'state': 'rejected'})

    def action_reset_draft(self):
        self.write({'state': 'draft'})

    def action_create_student(self):
        self.ensure_one()
        if self.student_id:
            return self.student_id.action_open_form()
        student = self.env['mindlab.student'].create({
            'name': self.student_name,
            'admission_id': self.id,
            'partner_id': self.parent_id.id,
            'guardian_name': self.guardian_name,
            'mobile': self.mobile,
            'email': self.email,
            'address': self.address,
            'birth_date': self.birth_date,
            'current_stage_id': self.desired_stage_id.id,
        })
        self.student_id = student.id
        return student.action_open_form()

    def action_mark_enrolled(self):
        for rec in self:
            if not rec.student_id:
                raise UserError('Please create a student before marking admission as enrolled.')
            rec.state = 'enrolled'

    def action_view_enrollments(self):
        self.ensure_one()
        return {
            'name': 'Enrollments',
            'type': 'ir.actions.act_window',
            'res_model': 'mindlab.enrollment',
            'view_mode': 'list,form',
            'domain': [('admission_id', '=', self.id)],
            'context': {'default_admission_id': self.id, 'default_student_id': self.student_id.id},
        }

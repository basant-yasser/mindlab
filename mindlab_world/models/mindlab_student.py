from datetime import date

from odoo import api, fields, models


class MindlabStudent(models.Model):
    _name = 'mindlab.student'
    _description = 'Mindlab Student'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(required=True, tracking=True)
    student_code = fields.Char(default='New', copy=False, readonly=True)
    admission_id = fields.Many2one('mindlab.admission')
    admission_ids = fields.One2many('mindlab.admission', 'student_id')
    active = fields.Boolean(default=True)
    image_1920 = fields.Image()
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')])
    birth_date = fields.Date()
    age = fields.Integer(compute='_compute_age', store=True)
    nationality = fields.Char()
    partner_id = fields.Many2one('res.partner', string='Parent / Guardian')
    father_name = fields.Char()
    mother_name = fields.Char()
    guardian_name = fields.Char()
    mobile = fields.Char()
    email = fields.Char()
    address = fields.Text()
    school_name = fields.Char()
    academic_notes = fields.Text()
    medical_notes = fields.Text()
    allergy_notes = fields.Text()
    emergency_contact = fields.Char()
    state = fields.Selection([
        ('new', 'New'),
        ('active', 'Active'),
        ('graduated', 'Graduated'),
        ('inactive', 'Inactive'),
    ], default='new', tracking=True)
    current_stage_id = fields.Many2one('mindlab.stage', tracking=True)
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    notes = fields.Text()

    enrollment_ids = fields.One2many('mindlab.enrollment', 'student_id')
    evaluation_ids = fields.One2many('mindlab.student.evaluation', 'student_id')
    attendance_ids = fields.One2many('mindlab.attendance', 'student_id')
    progression_ids = fields.One2many('mindlab.student.progression', 'student_id')
    session_log_ids = fields.One2many('mindlab.session.log', 'student_id')
    invoice_ids = fields.One2many('account.move', 'mindlab_student_id')

    enrollment_count = fields.Integer(compute='_compute_counts')
    evaluation_count = fields.Integer(compute='_compute_counts')
    attendance_count = fields.Integer(compute='_compute_counts')
    progression_count = fields.Integer(compute='_compute_counts')
    invoice_count = fields.Integer(compute='_compute_counts')
    admission_count = fields.Integer(compute='_compute_counts')
    total_remaining_sessions = fields.Integer(compute='_compute_total_remaining_sessions', store=True)
    latest_evaluation_id = fields.Many2one('mindlab.student.evaluation', compute='_compute_latest_evaluation')

    @api.model_create_multi
    def create(self, vals_list):
        seq = self.env['ir.sequence']
        for vals in vals_list:
            if vals.get('student_code', 'New') == 'New':
                vals['student_code'] = seq.next_by_code('mindlab.student') or 'New'
        return super().create(vals_list)

    @api.depends('birth_date')
    def _compute_age(self):
        today = date.today()
        for rec in self:
            if rec.birth_date:
                rec.age = today.year - rec.birth_date.year - ((today.month, today.day) < (rec.birth_date.month, rec.birth_date.day))
            else:
                rec.age = 0

    @api.depends('enrollment_ids', 'evaluation_ids', 'attendance_ids', 'progression_ids', 'invoice_ids', 'admission_ids')
    def _compute_counts(self):
        for rec in self:
            rec.enrollment_count = len(rec.enrollment_ids)
            rec.evaluation_count = len(rec.evaluation_ids)
            rec.attendance_count = len(rec.attendance_ids)
            rec.progression_count = len(rec.progression_ids)
            rec.invoice_count = len(rec.invoice_ids)
            rec.admission_count = len(rec.admission_ids)

    @api.depends('enrollment_ids.remaining_sessions')
    def _compute_total_remaining_sessions(self):
        for rec in self:
            rec.total_remaining_sessions = int(sum(rec.enrollment_ids.filtered(lambda e: e.state == 'active').mapped('remaining_sessions')))

    @api.depends('evaluation_ids', 'evaluation_ids.evaluation_date')
    def _compute_latest_evaluation(self):
        for rec in self:
            rec.latest_evaluation_id = rec.evaluation_ids.sorted(lambda ev: (ev.evaluation_date or fields.Date.today(), ev.id), reverse=True)[:1]

    def action_open_form(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'mindlab.student',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def _smart_action(self, model, domain):
        self.ensure_one()
        return {'name': model, 'type': 'ir.actions.act_window', 'res_model': model, 'view_mode': 'list,form', 'domain': domain}

    def action_view_admissions(self):
        return self._smart_action('mindlab.admission', [('student_id', '=', self.id)])

    def action_view_enrollments(self):
        return self._smart_action('mindlab.enrollment', [('student_id', '=', self.id)])

    def action_view_evaluations(self):
        return self._smart_action('mindlab.student.evaluation', [('student_id', '=', self.id)])

    def action_view_attendance(self):
        return self._smart_action('mindlab.attendance', [('student_id', '=', self.id)])

    def action_view_progressions(self):
        return self._smart_action('mindlab.student.progression', [('student_id', '=', self.id)])

    def action_view_invoices(self):
        return self._smart_action('account.move', [('mindlab_student_id', '=', self.id), ('move_type', '=', 'out_invoice')])

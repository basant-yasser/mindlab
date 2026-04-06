from odoo import api, fields, models


class MindlabAttendance(models.Model):
    _name = 'mindlab.attendance'
    _description = 'Mindlab Attendance'
    _order = 'date desc, id desc'

    enrollment_id = fields.Many2one('mindlab.enrollment', required=True, ondelete='cascade')
    student_id = fields.Many2one('mindlab.student', required=True)
    offer_id = fields.Many2one('mindlab.offer', required=True)
    teacher_id = fields.Many2one('res.users')
    date = fields.Date(default=fields.Date.context_today, required=True)
    attendance_state = fields.Selection([
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('excused', 'Excused'),
        ('no_show', 'No Show'),
    ], default='present', required=True)
    deduct_session = fields.Boolean(default=False)
    notes = fields.Text()
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    session_log_id = fields.Many2one('mindlab.session.log', readonly=True, copy=False)
    batch_id = fields.Many2one('mindlab.attendance.batch', ondelete='set null', index=True, copy=False)

    _mindlab_attendance_unique_day = models.Constraint(
        'UNIQUE(enrollment_id, student_id, date)',
        'Attendance already exists for this student and day in the enrollment.'
    )

    @api.onchange('enrollment_id', 'attendance_state')
    def _onchange_enrollment_id(self):
        for rec in self:
            if rec.enrollment_id:
                rec.student_id = rec.enrollment_id.student_id
                rec.offer_id = rec.enrollment_id.offer_id
                rec.teacher_id = rec.enrollment_id.teacher_id
                rec.deduct_session = rec.enrollment_id.should_deduct_for_state(rec.attendance_state, False)

    def _log_session_action(self, action_type, reason):
        self.ensure_one()
        enrollment = self.enrollment_id
        before = enrollment.remaining_sessions
        qty = 1.0
        self.env['mindlab.session.log'].create({
            'enrollment_id': enrollment.id,
            'student_id': self.student_id.id,
            'attendance_id': self.id,
            'action_type': action_type,
            'qty': qty,
            'reason': reason,
            'before_remaining': before,
            'after_remaining': before - qty if action_type == 'consume' else before + qty,
        })

    def _sync_session_consumption(self):
        for rec in self:
            should_deduct = rec.enrollment_id.should_deduct_for_state(rec.attendance_state, rec.deduct_session)
            if should_deduct and not rec.session_log_id:
                rec._log_session_action('consume', f'Attendance {rec.attendance_state} on {rec.date}')
                rec.session_log_id = self.env['mindlab.session.log'].search([('attendance_id', '=', rec.id), ('action_type', '=', 'consume')], limit=1)
            elif not should_deduct and rec.session_log_id:
                rec._log_session_action('restore', f'Reversal of attendance deduction for {rec.date}')
                rec.session_log_id = False

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('enrollment_id') and 'deduct_session' not in vals:
                enrollment = self.env['mindlab.enrollment'].browse(vals['enrollment_id'])
                vals['deduct_session'] = enrollment.should_deduct_for_state(vals.get('attendance_state', 'present'), False)
        records = super().create(vals_list)
        records._sync_session_consumption()
        return records

    def write(self, vals):
        res = super().write(vals)
        self._sync_session_consumption()
        return res

    def unlink(self):
        for rec in self:
            if rec.session_log_id:
                rec._log_session_action('restore', f'Restored because attendance {rec.date} was deleted')
        return super().unlink()


class MindlabAttendanceBatch(models.Model):
    _name = 'mindlab.attendance.batch'
    _description = 'Mindlab Attendance Batch'
    _order = 'date desc, id desc'

    name = fields.Char(default='New', readonly=True, copy=False)
    date = fields.Date(default=fields.Date.context_today, required=True)
    offer_id = fields.Many2one('mindlab.offer', required=True)
    teacher_id = fields.Many2one('res.users')
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    line_ids = fields.One2many('mindlab.attendance.batch.line', 'batch_id', copy=True)
    notes = fields.Text()

    @api.model_create_multi
    def create(self, vals_list):
        seq = self.env['ir.sequence']
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = seq.next_by_code('mindlab.attendance.batch') or 'New'
        recs = super().create(vals_list)
        recs._sync_attendance_lines()
        return recs

    def write(self, vals):
        res = super().write(vals)
        self._sync_attendance_lines()
        return res

    @api.onchange('offer_id')
    def _onchange_offer_id(self):
        for rec in self:
            if not rec.offer_id:
                continue
            rec.teacher_id = rec.offer_id.teacher_id
            if rec.line_ids:
                continue
            enrollments = self.env['mindlab.enrollment'].search([
                ('offer_id', '=', rec.offer_id.id),
                ('state', 'in', ['draft', 'active', 'suspended']),
            ])
            rec.line_ids = [(0, 0, {'enrollment_id': enrollment.id}) for enrollment in enrollments]

    def action_open_add_students_wizard(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Add Students',
            'res_model': 'mindlab.attendance.batch.add.students.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'active_id': self.id,
                'default_batch_id': self.id,
                'default_offer_id': self.offer_id.id,
            },
        }

    def _sync_attendance_lines(self):
        Attendance = self.env['mindlab.attendance']
        for rec in self:
            linked_attendance = rec.line_ids.mapped('attendance_id')
            stale_attendance = Attendance.search([('batch_id', '=', rec.id), ('id', 'not in', linked_attendance.ids)])
            if stale_attendance:
                stale_attendance.unlink()
            for line in rec.line_ids:
                line._sync_attendance_record()


class MindlabAttendanceBatchLine(models.Model):
    _name = 'mindlab.attendance.batch.line'
    _description = 'Mindlab Attendance Batch Line'
    _order = 'id'

    batch_id = fields.Many2one('mindlab.attendance.batch', required=True, ondelete='cascade')
    enrollment_id = fields.Many2one('mindlab.enrollment', required=True, domain="[('offer_id', '=', parent.offer_id)]")
    student_id = fields.Many2one('mindlab.student', related='enrollment_id.student_id', store=True, readonly=True)
    current_stage_id = fields.Many2one('mindlab.stage', related='student_id.current_stage_id', store=True, readonly=True)
    attendance_state = fields.Selection([
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('excused', 'Excused'),
        ('no_show', 'No Show'),
    ], default='present', required=True)
    deduct_session = fields.Boolean(default=False)
    attendance_id = fields.Many2one('mindlab.attendance', readonly=True, copy=False)

    @api.onchange('enrollment_id', 'attendance_state')
    def _onchange_enrollment_id(self):
        for rec in self:
            if rec.enrollment_id:
                rec.deduct_session = rec.enrollment_id.should_deduct_for_state(rec.attendance_state, False)

    def _sync_attendance_record(self):
        self.ensure_one()
        vals = {
            'date': self.batch_id.date,
            'enrollment_id': self.enrollment_id.id,
            'student_id': self.student_id.id,
            'offer_id': self.batch_id.offer_id.id,
            'teacher_id': self.batch_id.teacher_id.id,
            'attendance_state': self.attendance_state,
            'deduct_session': self.deduct_session,
            'notes': self.batch_id.notes,
            'company_id': self.batch_id.company_id.id,
            'batch_id': self.batch_id.id,
        }
        if self.attendance_id:
            self.attendance_id.write(vals)
            return
        attendance = self.env['mindlab.attendance'].search([
            ('enrollment_id', '=', self.enrollment_id.id),
            ('student_id', '=', self.student_id.id),
            ('date', '=', self.batch_id.date),
        ], limit=1)
        if attendance:
            attendance.write(vals)
        else:
            attendance = self.env['mindlab.attendance'].create(vals)
        self.attendance_id = attendance.id

    def unlink(self):
        linked = self.mapped('attendance_id')
        res = super().unlink()
        if linked:
            linked.unlink()
        return res

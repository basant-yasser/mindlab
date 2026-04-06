from odoo import api, fields, models
from odoo.exceptions import UserError


class MindlabEnrollment(models.Model):
    _name = 'mindlab.enrollment'
    _description = 'Mindlab Enrollment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(default='New', readonly=True, copy=False)
    student_id = fields.Many2one('mindlab.student', required=True, tracking=True)
    admission_id = fields.Many2one('mindlab.admission')
    offer_id = fields.Many2one('mindlab.offer', required=True, tracking=True)
    offer_type = fields.Selection(related='offer_id.offer_type', store=True)
    teacher_id = fields.Many2one('res.users')
    start_date = fields.Date(default=fields.Date.context_today, required=True)
    end_date = fields.Date()
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('suspended', 'Suspended'),
    ], default='draft', tracking=True)
    fee = fields.Monetary(currency_field='currency_id', required=True, default=0.0)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', store=True, readonly=True)
    invoice_status = fields.Selection([
        ('no', 'Not Invoiced'),
        ('invoiced', 'Invoiced'),
        ('paid', 'Paid'),
    ], compute='_compute_invoice_status', store=True)
    invoice_id = fields.Many2one('account.move', copy=False, readonly=True)
    total_sessions = fields.Integer(compute='_compute_sessions', store=True)
    used_sessions = fields.Float(compute='_compute_sessions', store=True)
    remaining_sessions = fields.Float(compute='_compute_sessions', store=True)
    attendance_policy = fields.Selection([
        ('settings', 'Use Settings'),
        ('present_only', 'Present Only'),
        ('present_absent', 'Present + Absent'),
        ('present_absent_excused', 'Present + Absent + Excused'),
    ], default='settings', required=True)
    notes = fields.Text()
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)

    attendance_ids = fields.One2many('mindlab.attendance', 'enrollment_id')
    session_log_ids = fields.One2many('mindlab.session.log', 'enrollment_id')

    @api.model_create_multi
    def create(self, vals_list):
        seq = self.env['ir.sequence']
        for vals in vals_list:
            if not vals.get('attendance_policy'):
                vals['attendance_policy'] = 'settings'
            if vals.get('name', 'New') == 'New':
                vals['name'] = seq.next_by_code('mindlab.enrollment') or 'New'
            if not vals.get('fee') and vals.get('offer_id'):
                offer = self.env['mindlab.offer'].browse(vals['offer_id'])
                vals['fee'] = offer.fee
            if not vals.get('teacher_id') and vals.get('offer_id'):
                offer = self.env['mindlab.offer'].browse(vals['offer_id'])
                vals['teacher_id'] = offer.teacher_id.id
        recs = super().create(vals_list)
        auto_invoice = self.env['ir.config_parameter'].sudo().get_param('mindlab_world.auto_invoice_on_enrollment', 'False') == 'True'
        if auto_invoice:
            for rec in recs.filtered(lambda r: r.state in ('draft', 'active')):
                rec.action_generate_invoice()
        return recs

    @api.depends('invoice_id.state', 'invoice_id.payment_state')
    def _compute_invoice_status(self):
        for rec in self:
            if not rec.invoice_id:
                rec.invoice_status = 'no'
            elif rec.invoice_id.payment_state in ('paid', 'in_payment'):
                rec.invoice_status = 'paid'
            else:
                rec.invoice_status = 'invoiced'

    @api.depends('offer_id.total_sessions', 'offer_id.has_session_limit', 'session_log_ids.action_type', 'session_log_ids.qty')
    def _compute_sessions(self):
        for rec in self:
            total = rec.offer_id.total_sessions if rec.offer_id.has_session_limit else 0
            consumed = sum(rec.session_log_ids.filtered(lambda l: l.action_type == 'consume').mapped('qty'))
            restored = sum(rec.session_log_ids.filtered(lambda l: l.action_type == 'restore').mapped('qty'))
            manual = sum(rec.session_log_ids.filtered(lambda l: l.action_type == 'manual_adjustment').mapped('qty'))
            used = consumed - restored + manual
            rec.total_sessions = total
            rec.used_sessions = used
            rec.remaining_sessions = total - used if rec.offer_id.has_session_limit else 0

    @api.onchange('offer_id')
    def _onchange_offer_id(self):
        for rec in self:
            if rec.offer_id:
                rec.fee = rec.offer_id.fee
                rec.teacher_id = rec.offer_id.teacher_id

    def _get_config_deductions(self):
        icp = self.env['ir.config_parameter'].sudo()
        return {
            'present': icp.get_param('mindlab_world.deduct_present', 'True') == 'True',
            'absent': icp.get_param('mindlab_world.deduct_absent', 'False') == 'True',
            'excused': icp.get_param('mindlab_world.deduct_excused', 'False') == 'True',
        }

    def should_deduct_for_state(self, attendance_state, force_deduct=False):
        self.ensure_one()
        if force_deduct:
            return True
        if not self.offer_id.has_session_limit:
            return False
        if self.remaining_sessions <= 0:
            return False
        if self.attendance_policy == 'present_only':
            return attendance_state == 'present'
        if self.attendance_policy == 'present_absent':
            return attendance_state in ('present', 'absent')
        if self.attendance_policy == 'present_absent_excused':
            return attendance_state in ('present', 'absent', 'excused')
        default_policy = self.env['ir.config_parameter'].sudo().get_param('mindlab_world.default_attendance_deduction_mode', 'present_only')
        if default_policy == 'present_only':
            return attendance_state == 'present'
        if default_policy == 'present_absent':
            return attendance_state in ('present', 'absent')
        if default_policy == 'present_absent_excused':
            return attendance_state in ('present', 'absent', 'excused')
        flags = self._get_config_deductions()
        return flags.get(attendance_state, False)

    def action_activate(self):
        self.write({'state': 'active'})

    def action_complete(self):
        self.write({'state': 'completed'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_suspend(self):
        self.write({'state': 'suspended'})

    def action_reset_draft(self):
        self.write({'state': 'draft'})

    def action_generate_invoice(self):
        for rec in self:
            if rec.invoice_id:
                continue
            partner = rec.student_id.partner_id
            if not partner:
                raise UserError('Please set a parent/guardian partner on the student before invoicing.')
            line_vals = {
                'name': rec.offer_id.name,
                'quantity': 1.0,
                'price_unit': rec.fee,
            }
            if rec.offer_id.product_id:
                line_vals['product_id'] = rec.offer_id.product_id.id
                line_vals['name'] = rec.offer_id.product_id.display_name
            invoice = self.env['account.move'].create({
                'move_type': 'out_invoice',
                'partner_id': partner.id,
                'invoice_date': fields.Date.context_today(self),
                'invoice_line_ids': [(0, 0, line_vals)],
                'mindlab_student_id': rec.student_id.id,
                'mindlab_enrollment_id': rec.id,
            })
            rec.invoice_id = invoice.id
        return True

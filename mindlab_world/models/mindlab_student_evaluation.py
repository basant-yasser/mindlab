from odoo import api, fields, models


class MindlabStudentEvaluation(models.Model):
    _name = 'mindlab.student.evaluation'
    _description = 'Mindlab Student Evaluation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'evaluation_date desc, id desc'

    name = fields.Char(default='New', readonly=True, copy=False)
    student_id = fields.Many2one('mindlab.student', required=True, tracking=True)
    enrollment_id = fields.Many2one('mindlab.enrollment')
    offer_id = fields.Many2one('mindlab.offer', required=True)
    evaluation_template_id = fields.Many2one('mindlab.evaluation.template')
    evaluation_date = fields.Date(default=fields.Date.context_today, required=True)
    teacher_id = fields.Many2one('res.users')
    total_score = fields.Float(compute='_compute_total_score', store=True)
    result = fields.Selection([
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('needs_support', 'Needs Support'),
    ], compute='_compute_total_score', store=True)
    notes = fields.Text()
    recommendation = fields.Text()
    stage_from_id = fields.Many2one('mindlab.stage')
    stage_to_id = fields.Many2one('mindlab.stage')
    progressed = fields.Boolean(default=False)
    line_ids = fields.One2many('mindlab.student.evaluation.line', 'evaluation_id')
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')], default='draft', tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        seq = self.env['ir.sequence']
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = seq.next_by_code('mindlab.student.evaluation') or 'New'
        return super().create(vals_list)

    @api.depends('line_ids.score', 'line_ids.max_score')
    def _compute_total_score(self):
        for rec in self:
            total = sum(rec.line_ids.mapped('score'))
            max_total = sum(rec.line_ids.mapped('max_score')) or 1
            percent = (total / max_total) * 100
            rec.total_score = total
            if percent >= 85:
                rec.result = 'excellent'
            elif percent >= 60:
                rec.result = 'good'
            else:
                rec.result = 'needs_support'

    @api.onchange('evaluation_template_id')
    def _onchange_template(self):
        for rec in self:
            if rec.evaluation_template_id and not rec.line_ids:
                rec.line_ids = [(0, 0, {
                    'criterion': line.criterion_name,
                    'max_score': line.max_score,
                }) for line in rec.evaluation_template_id.line_ids]

    @api.onchange('enrollment_id')
    def _onchange_enrollment(self):
        for rec in self:
            if rec.enrollment_id:
                rec.offer_id = rec.enrollment_id.offer_id
                rec.teacher_id = rec.enrollment_id.teacher_id

    def action_mark_done(self):
        enable_progression = self.env['ir.config_parameter'].sudo().get_param('mindlab_world.enable_progression_tracking', 'True') == 'True'
        require_eval = self.env['ir.config_parameter'].sudo().get_param('mindlab_world.require_evaluation_for_progression', 'False') == 'True'
        for rec in self:
            rec.state = 'done'
            if rec.progressed and rec.stage_to_id and enable_progression:
                if require_eval and not rec.line_ids:
                    continue
                progression = self.env['mindlab.student.progression'].search([('evaluation_id', '=', rec.id)], limit=1)
                if not progression:
                    self.env['mindlab.student.progression'].create({
                        'student_id': rec.student_id.id,
                        'from_stage_id': rec.stage_from_id.id or rec.student_id.current_stage_id.id,
                        'to_stage_id': rec.stage_to_id.id,
                        'date': rec.evaluation_date,
                        'evaluation_id': rec.id,
                        'reason': 'Evaluation progression',
                    })
                rec.student_id.current_stage_id = rec.stage_to_id


class MindlabStudentEvaluationLine(models.Model):
    _name = 'mindlab.student.evaluation.line'
    _description = 'Mindlab Student Evaluation Line'
    _order = 'id'

    evaluation_id = fields.Many2one('mindlab.student.evaluation', required=True, ondelete='cascade')
    criterion = fields.Char(required=True)
    score = fields.Float(default=0.0)
    max_score = fields.Float(default=100.0)
    remarks = fields.Char()

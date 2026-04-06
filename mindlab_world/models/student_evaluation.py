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
    total_score = fields.Float(compute='_compute_totals', store=True)
    performance_level = fields.Selection([
        ('needs_support', 'Needs Support'),
        ('emerging', 'Emerging'),
        ('developing', 'Developing'),
        ('achieved', 'Achieved'),
    ], compute='_compute_totals', store=True)
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

    @api.depends('line_ids.weighted_score')
    def _compute_totals(self):
        for rec in self:
            rec.total_score = sum(rec.line_ids.mapped('weighted_score'))
            if rec.total_score >= 85:
                rec.performance_level = 'achieved'
            elif rec.total_score >= 70:
                rec.performance_level = 'developing'
            elif rec.total_score >= 50:
                rec.performance_level = 'emerging'
            else:
                rec.performance_level = 'needs_support'

    @api.onchange('evaluation_template_id')
    def _onchange_template(self):
        for rec in self:
            if not rec.evaluation_template_id:
                rec.line_ids = [(5, 0, 0)]
                continue

            # Preserve entered scores/notes unless the template itself changed.
            if rec._origin and rec.evaluation_template_id == rec._origin.evaluation_template_id:
                continue

            rec.line_ids = [(5, 0, 0)]
            rec.line_ids = [(0, 0, {
                'criterion_id': line.id,
                'weight': line.weight,
            }) for line in rec.evaluation_template_id.line_ids.sorted('sequence')]

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
    criterion_id = fields.Many2one('mindlab.evaluation.template.line', required=True)
    criterion_name = fields.Char(related='criterion_id.criterion_name', store=True)
    weight = fields.Float(default=0.0)
    score = fields.Selection([
        ('1', '1 – Not Yet'),
        ('2', '2 – Emerging'),
        ('3', '3 – Developing'),
        ('4', '4 – Achieved'),
    ], string='Score (1-4)', required=True)
    notes = fields.Char()
    weighted_score = fields.Float(compute='_compute_weighted_score', store=True)

    @api.depends('weight', 'score')
    def _compute_weighted_score(self):
        for rec in self:
            score_value = float(rec.score or 0.0)
            rec.weighted_score = (rec.weight * score_value) / 4

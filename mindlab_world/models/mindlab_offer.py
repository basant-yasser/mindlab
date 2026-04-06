from odoo import api, fields, models


class MindlabOffer(models.Model):
    _name = 'mindlab.offer'
    _description = 'Mindlab Educational Offering'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'display_name'

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(required=True, tracking=True)
    active = fields.Boolean(default=True)
    offer_type = fields.Selection([
        ('program', 'Program'),
        ('course', 'Course'),
    ], required=True, default='program', tracking=True)
    category_id = fields.Many2one('mindlab.category')
    stage_id = fields.Many2one('mindlab.stage', tracking=True)
    teacher_id = fields.Many2one('res.users', tracking=True)
    duration_value = fields.Integer(default=1)
    duration_unit = fields.Selection([
        ('days', 'Days'),
        ('weeks', 'Weeks'),
        ('months', 'Months'),
    ], default='weeks', required=True)
    total_sessions = fields.Integer(default=0)
    has_session_limit = fields.Boolean(default=False)
    fee = fields.Monetary(currency_field='currency_id', required=True, default=0.0)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', store=True, readonly=True)
    product_id = fields.Many2one('product.product', domain=[('sale_ok', '=', True)])
    allow_evaluation = fields.Boolean(default=True)
    evaluation_template_id = fields.Many2one('mindlab.evaluation.template')
    parent_program_id = fields.Many2one('mindlab.offer', domain=[('offer_type', '=', 'program')])
    description = fields.Html()
    notes = fields.Text()
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    display_name = fields.Char(compute='_compute_display_name', store=True)

    _mindlab_offer_code_company_unique = models.Constraint(
        'UNIQUE(code, company_id)',
        'Offer code must be unique per company.'
    )

    @api.depends('name', 'code')
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"[{rec.code}] {rec.name}" if rec.code else rec.name

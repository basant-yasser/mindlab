from odoo import api, fields, models

SCORE_SELECTION = [
    ("1", "1 - Not Yet"),
    ("2", "2 - Emerging"),
    ("3", "3 - Developing"),
    ("4", "4 - Achieved"),
]

class NurseryAssessment(models.Model):
    _name = "nursery.assessment"
    _description = "Student Assessment"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"

    name = fields.Char(default="New", readonly=True, copy=False)
    date = fields.Date(default=fields.Date.context_today, required=True, tracking=True)

    student_id = fields.Many2one(
        "res.partner",
        string="Student",
        required=True,
        domain=[("is_company", "=", False)],
        tracking=True,
    )
    teacher_id = fields.Many2one("res.users", default=lambda self: self.env.user, required=True, tracking=True)

    rubric_id = fields.Many2one("nursery.rubric", required=True, tracking=True)
    line_ids = fields.One2many("nursery.assessment.line", "assessment_id", string="Rubric Lines", copy=False)

    total_score = fields.Float(string="Total (/100)", compute="_compute_total", store=True, tracking=True)
    performance_level = fields.Selection(
        [("low", "Needs Support"), ("mid", "Developing"), ("high", "Achieved")],
        compute="_compute_level",
        store=True,
    )

    state = fields.Selection(
        [("draft", "Draft"), ("submitted", "Submitted"), ("approved", "Approved")],
        default="draft",
        tracking=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if rec.name == "New":
                rec.name = self.env["ir.sequence"].next_by_code("nursery.assessment") or f"ASM/{rec.id}"
        return records

    @api.onchange("rubric_id")
    def _onchange_rubric_id(self):
        if not self.rubric_id:
            self.line_ids = [(5, 0, 0)]
            return

        lines_cmd = [(5, 0, 0)]
        for tline in self.rubric_id.line_ids:
            lines_cmd.append((0, 0, {
                "criterion_name": tline.name,
                "weight": tline.weight,
                "level_1": tline.level_1,
                "level_2": tline.level_2,
                "level_3": tline.level_3,
                "level_4": tline.level_4,
                "sequence": tline.sequence,
            }))
        self.line_ids = lines_cmd

    @api.depends("line_ids.weighted_score")
    def _compute_total(self):
        for rec in self:
            rec.total_score = sum(rec.line_ids.mapped("weighted_score"))

    @api.depends("total_score")
    def _compute_level(self):
        for rec in self:
            if rec.total_score < 50:
                rec.performance_level = "low"
            elif rec.total_score < 75:
                rec.performance_level = "mid"
            else:
                rec.performance_level = "high"

    def action_submit(self):
        self.write({"state": "submitted"})

    def action_approve(self):
        self.write({"state": "approved"})


class NurseryAssessmentLine(models.Model):
    _name = "nursery.assessment.line"
    _description = "Assessment Line"
    _order = "sequence, id"

    assessment_id = fields.Many2one("nursery.assessment", required=True, ondelete="cascade")

    sequence = fields.Integer(default=10)
    criterion_name = fields.Char(required=True)
    weight = fields.Float(required=True, string="Weight (%)")

    score = fields.Selection(SCORE_SELECTION, string="Score (1-4)")
    weighted_score = fields.Float(string="Weighted", compute="_compute_weighted", store=True)

    notes = fields.Char(string="Notes")

    # snapshot of rubric level descriptions (kept for stable historical reporting)
    level_1 = fields.Text()
    level_2 = fields.Text()
    level_3 = fields.Text()
    level_4 = fields.Text()

    @api.depends("score", "weight")
    def _compute_weighted(self):
        for line in self:
            if not line.score:
                line.weighted_score = 0.0
            else:
                line.weighted_score = (int(line.score) / 4.0) * line.weight

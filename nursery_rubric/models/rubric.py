from odoo import api, fields, models
from odoo.exceptions import ValidationError

class NurseryRubric(models.Model):
    _name = "nursery.rubric"
    _description = "Rubric Template"
    _order = "name"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    note = fields.Text(string="Internal Notes")

    line_ids = fields.One2many("nursery.rubric.line", "rubric_id", string="Criteria")
    weight_total = fields.Float(string="Total Weight (%)", compute="_compute_weight_total", store=True)

    @api.depends("line_ids.weight")
    def _compute_weight_total(self):
        for rec in self:
            rec.weight_total = sum(rec.line_ids.mapped("weight"))

    @api.constrains("line_ids", "line_ids.weight")
    def _check_weights_sum(self):
        for rec in self:
            if rec.line_ids and abs(rec.weight_total - 100.0) > 0.0001:
                raise ValidationError("Rubric weights must sum to 100%.")

class NurseryRubricLine(models.Model):
    _name = "nursery.rubric.line"
    _description = "Rubric Criterion"
    _order = "sequence, id"

    rubric_id = fields.Many2one("nursery.rubric", required=True, ondelete="cascade")
    sequence = fields.Integer(default=10)

    name = fields.Char(required=True, string="Criterion")
    weight = fields.Float(required=True, string="Weight (%)")

    level_1 = fields.Text(string="1 - Not Yet")
    level_2 = fields.Text(string="2 - Emerging")
    level_3 = fields.Text(string="3 - Developing")
    level_4 = fields.Text(string="4 - Achieved")

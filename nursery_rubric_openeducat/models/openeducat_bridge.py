from odoo import api, fields, models
from odoo.exceptions import UserError


class OpCourse(models.Model):
    _inherit = "op.course"

    rubric_id = fields.Many2one(
        "nursery.rubric",
        string="Rubric Template",
        help="Rubric used to assess students in this course."
    )


class NurseryAssessment(models.Model):
    _inherit = "nursery.assessment"

    course_id = fields.Many2one("op.course", string="Course", tracking=True)
    op_student_id = fields.Many2one("op.student", string="Student", tracking=True)

    # Contact-based student optional; sync from OpenEduCat student if partner_id exists
    student_id = fields.Many2one(
        "res.partner",
        string="Student (Contact)",
        domain=[("is_company", "=", False)],
        required=False,
        tracking=True,
    )

    @api.onchange("course_id")
    def _onchange_course_id(self):
        if self.course_id and self.course_id.rubric_id:
            self.rubric_id = self.course_id.rubric_id
            self._onchange_rubric_id()

    @api.onchange("op_student_id")
    def _onchange_op_student_id(self):
        if self.op_student_id and getattr(self.op_student_id, "partner_id", False):
            self.student_id = self.op_student_id.partner_id

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("op_student_id") and not vals.get("student_id"):
                st = self.env["op.student"].browse(vals["op_student_id"])
                if st and getattr(st, "partner_id", False):
                    vals["student_id"] = st.partner_id.id
        return super().create(vals_list)

    def write(self, vals):
        if vals.get("op_student_id") and not vals.get("student_id"):
            st = self.env["op.student"].browse(vals["op_student_id"])
            if st and getattr(st, "partner_id", False):
                vals["student_id"] = st.partner_id.id
        return super().write(vals)


class OpStudent(models.Model):
    _inherit = "op.student"

    assessment_ids = fields.One2many("nursery.assessment", "op_student_id", string="Assessments")

    def action_view_assessments(self):
        self.ensure_one()
        action = self.env.ref("nursery_rubric.action_nursery_assessment").read()[0]
        action["domain"] = [("op_student_id", "=", self.id)]
        action["context"] = dict(self.env.context, default_op_student_id=self.id)
        return action

    def action_print_latest_assessment(self):
        self.ensure_one()
        Assessment = self.env["nursery.assessment"]
        rec = Assessment.search(
            [("op_student_id", "=", self.id), ("state", "=", "approved")],
            order="date desc, id desc",
            limit=1
        )
        if not rec:
            rec = Assessment.search(
                [("op_student_id", "=", self.id)],
                order="date desc, id desc",
                limit=1
            )
        if not rec:
            raise UserError("No assessments found for this student yet.")
        return self.env.ref("nursery_rubric.action_report_nursery_assessment").report_action(rec)

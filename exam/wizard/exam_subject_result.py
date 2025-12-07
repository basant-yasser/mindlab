# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class SubjectResultWiz(models.TransientModel):
    _name = "subject.result.wiz"
    _description = "Subject Wise Result"

    result_ids = fields.Many2many(
        "subject.subject",
        "subject_exam_result_wiz_rel",
        "exam_result_id",
        "subject_id",
        string="Exam Subjects",
        help="Select exam subjects",
        required=True,
    )
    s_exam_id = fields.Many2one(
        "exam.exam", string="Examination", required=True, help="Select Exam"
    )

    # Add fields for safe context usage
    active_id = fields.Integer(string="Active ID", default=lambda self: self._context.get('active_id'))
    active_model = fields.Char(string="Active Model", default=lambda self: self._context.get('active_model'))

    @api.model
    def default_get(self, fields_list):
        """Override default_get to get default subjects"""
        res = super(SubjectResultWiz, self).default_get(fields_list)
        active_id = self._context.get("active_id")
        active_model = self._context.get("active_model")

        if active_id and active_model == "school.teacher":
            teacher_rec = self.env["school.teacher"].browse(active_id)
            if teacher_rec:
                subject_ids = teacher_rec.subject_id.ids
                res.update({"result_ids": [(6, 0, subject_ids)]})

        return res


    def result_report(self):
        """Method to get the result report"""
        data = self.read()[0]
        return self.env.ref("exam.add_exam_result_id_qweb").report_action([], data=data)

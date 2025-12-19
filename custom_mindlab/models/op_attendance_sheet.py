from odoo import api, fields, models


class OpAttendanceSheet(models.Model):
    _inherit = "op.attendance.sheet"

    def attendance_done(self):
        res = super().attendance_done()

        StudentSheet = self.env['student.attendance.sheet']

        for sheet in self:
            course = sheet.session_id.course_id
            total_sessions = course.number_of_sessions or 0

            for line in sheet.attendance_line:
                # Count how many sessions already recorded for this student
                attended_count = StudentSheet.search_count([
                    ('op_student_id', '=', line.student_id.id),
                    ('course_name', '=', course.id),
                ])

                remaining_sessions = total_sessions - attended_count - 1
                if remaining_sessions < 0:
                    remaining_sessions = 0

                StudentSheet.create({
                    'op_student_id': line.student_id.id,
                    'course_name': course.id,
                    'number_of_sessions': total_sessions,
                    'remaining_of_sessions': remaining_sessions,
                    'start_date': fields.Date.today(),
                    'start_datetime': sheet.session_id.start_datetime,
                    'end_datetime': sheet.session_id.end_datetime,
                })

        return res



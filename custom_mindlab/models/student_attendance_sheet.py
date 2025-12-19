from odoo import models, fields, api


class StudentAttendanceSheet(models.Model):
    _name = 'student.attendance.sheet'

    op_student_id = fields.Many2one('op.student',string='Student')
    course_name = fields.Many2one('op.course', string='Course Name')
    number_of_sessions = fields.Integer(string=' Number of Sessions')
    remaining_of_sessions = fields.Integer(string=' Number of Sessions')
    start_date = fields.Date('Start Date')
    start_datetime = fields.Datetime('Start Time')
    end_datetime = fields.Datetime('Start Time')


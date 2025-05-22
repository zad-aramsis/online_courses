from odoo import models, fields, api
from odoo.exceptions import ValidationError


class OnlineStudent(models.Model):
    _name = 'online.student'
    _description = 'Course Student'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _inherits = {'res.partner': 'partner_id'}

    partner_id = fields.Many2one('res.partner', string='Contact Information',
                                 required=True, ondelete='restrict', auto_join=True)

    student_id_number = fields.Char(string='Student ID Number', copy=False)
    enrollment_date = fields.Date(string='Enrollment Date', default=fields.Date.today)

    enrolled_course_ids = fields.Many2many('online.course', 'online_course_student_rel',
                                           'student_id', 'course_id', string='Enrolled Courses')
    attended_session_ids = fields.Many2many('online.session', 'session_student_attend_rel',
                                            'student_id', 'session_id', string='Attended Sessions')
    completed_course_ids = fields.Many2many('online.course', 'online_completed_course_student_rel',
                                           'student_id', 'completed_course_id', string='Completed Courses',
                                            compute='_compute_completed_course_ids', store=True)

    # _sql_constraints = [
    #     ('partner_uniq', 'unique (partner_id)', 'Each partner can only be linked to one student record.'),
    #     ('student_id_number_uniq', 'unique (student_id_number)', 'Student ID Number must be unique, if provided.')
    # ]

    @api.depends('enrolled_course_ids', 'enrolled_course_ids.state')
    def _compute_completed_course_ids(self):
        for student in self:
            completed = student.enrolled_course_ids.filtered(lambda c: c.state == 'completed')
            student.completed_course_ids = completed

    @api.model
    def create(self, vals_list):
        vals_list['student_id_number'] = self.env['ir.sequence'].next_by_code('online.student.id.sequence') or '0000'

        students = super().create(vals_list)

        for student in self:
            if student.partner_id:
                student.partner_id.is_student = True
        return students

    def unlink(self):
        for student in self:
            if student.partner_id:
                student.partner_id.is_student = False
        res = super().unlink()
        return res

    def action_view_partner_profile(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('contacts.action_contacts')

        if self.partner_id:
            action['views'] = [(self.env.ref('base.view_partner_form').id, 'form')]
            action['res_id'] = self.partner_id.id
            return action
        else:
            raise ValidationError("No Partner Found for this Instructor.")

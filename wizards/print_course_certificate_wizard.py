from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PrintCourseCertificateWizard(models.TransientModel):
    _name = 'print.course.certificate.wizard'
    _description = 'Wizard to Print Course Certificate for a Student'

    course_id = fields.Many2one('online.course', string="Course", required=True, readonly=True,
                                default=lambda self: self.env.context.get('active_id'))
    allowed_student_ids = fields.Many2many('online.student', compute='_compute_allowed_students')
    student_id = fields.Many2one('online.student', string="Student", required=True,
                                 domain="[('id', 'in', allowed_student_ids)]")

    @api.depends('course_id')
    def _compute_allowed_students(self):
        for wizard in self:
            if wizard.course_id:
                wizard.allowed_student_ids = wizard.course_id.student_ids.ids
            else:
                wizard.allowed_student_ids = []

    def action_print_certificate(self):
        self.ensure_one()
        # Ensure the student has completed the course or remove this check if not desired
        if self.course_id not in self.student_id.completed_course_ids:
            raise UserError(_("This Student has not been Marked as having Completed this Course yet."))

        return self.env.ref('online_courses.action_report_course_student_certification').with_context(
            active_student_ids=[self.student_id.id]).report_action(self.course_id)

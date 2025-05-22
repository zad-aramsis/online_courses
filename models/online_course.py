from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class OnlineCourse(models.Model):
    _name = 'online.course'
    _description = 'Online Course'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True, help="Set active to false to archive the course instead of deleting it.")
    name = fields.Char(string='Course Title', required=True, tracking=True)
    sequence_id = fields.Char(string='Course ID', required=True, copy=False, default=lambda self: _('New'))
    description = fields.Text(string='Description')
    responsible_user_id = fields.Many2one('res.users', string='Responsible User',
                                          default=lambda self: self.env.user, tracking=True)
    company_id = fields.Many2one('res.company', string='Company', related='responsible_user_id.company_id', store=True)
    instructor_ids = fields.Many2many('online.instructor', 'online_course_instructor_rel', 'course_id', 'instructor_id',
                                      string='Instructors', tracking=True, ondelete='restrict')
    session_ids = fields.One2many('online.session', 'course_id', string='Sessions')
    student_ids = fields.Many2many('online.student', 'online_course_student_rel',
                                   'course_id', 'student_id', string='Students')

    start_date = fields.Date(string='Start Date', required=True, tracking=True)
    end_date = fields.Date(string='End Date', required=True, tracking=True)
    duration_days = fields.Integer('Duration (days)', compute='_compute_duration', store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)
    price = fields.Monetary('Price', currency_field='currency_id', default=1000.0)
    currency_id = fields.Many2one('res.currency', string='Currency', related='company_id.currency_id', store=True)
    total_sessions = fields.Integer(string="Total Sessions", compute='_compute_total_sessions', store=True)
    total_students = fields.Integer(string="Total Students", compute='_compute_total_students', store=True)
    instructor_notified = fields.Boolean(string="Instructor Notified", default=False, copy=False)

    @api.constrains('end_date', 'start_date')
    def _check_dates(self):
        for rec in self:
            if rec.end_date and rec.start_date and rec.end_date < rec.start_date:
                raise ValidationError('End Date cannot be before Start Date')

    @api.model
    def create(self, vals_list):
        vals_list['sequence_id'] = self.env['ir.sequence'].next_by_code('online.course.sequence') or _('New')
        return super().create(vals_list)

    @api.depends('start_date', 'end_date')
    def _compute_duration(self):
        for rec in self:
            if rec.start_date and rec.end_date:
                rec.duration_days = (rec.end_date - rec.start_date).days
            else:
                rec.duration_days = 0

    @api.depends('session_ids')
    def _compute_total_sessions(self):
        for course in self:
            course.total_sessions = len(course.session_ids)

    @api.depends('student_ids')
    def _compute_total_students(self):
        for course in self:
            course.total_students = len(course.student_ids)

    def action_confirm(self):
        for course in self:
            if not course.instructor_ids:
                raise UserError(_("No Instructors to Confirm."))
            if not self.session_ids:
                raise UserError(_("No Sessions to Confirm."))
            if not course.student_ids:
                raise UserError(_("No Students to Confirm."))
            course.state = 'in_progress'

    def action_complete(self):
        for course in self:
            if any(state != 'done' for state in course.session_ids.mapped('state')):
                raise UserError(_("All Sessions must be in 'Done' state to Mark the Course as Completed."))
            course.state = 'completed'

    def action_cancel(self):
        for course in self:
            course.state = 'cancelled'

    def action_reset_to_draft(self):
        for course in self:
            course.state = 'draft'

    def _cron_notify_instructor_assignment(self):
        courses_to_notify = self.search([
            ('instructor_ids', '!=', False),
            ('instructor_notified', '=', False),
            ('state', '=', 'draft')
        ])
        for course in courses_to_notify:
            if course.instructor_ids:
                template = self.env.ref('online_courses.email_template_instructor_assignment', raise_if_not_found=False)
                if template:
                    email_values = {'recipient_ids': [(4, pid.partner_id.id) for pid in course.instructor_ids]}
                    template.send_mail(course.id, force_send=True, email_values=email_values)
                    course.instructor_notified = True
                else:
                    _logger.warning(
                        f"Email template 'email_template_instructor_assignment' not found for course {course.name}")
        return True

    def action_create_course_sessions(self):
        for course in self:
            if course.state == 'draft':
                if course.instructor_ids:
                    for instructor in course.instructor_ids:
                        course.session_ids.create({
                            'name': f"{course.name} - Session by {instructor.name}",
                            'course_id': course.id,
                            'instructor_id': instructor.id,
                            'start_datetime': fields.Datetime.now(),
                            'duration': 3,
                            'seats': course.total_students or 20,
                        })
                else:
                    raise UserError(_("This is no Instructors to Create Sessions for."))
            else:
                raise UserError(_("You can only Create Sessions for Draft Courses."))
        return True

    def action_view_session_list(self):
        self.ensure_one()

        if self.session_ids:
            action = self.env['ir.actions.act_window']._for_xml_id('online_courses.action_online_session_list')
            action['domain'] = [('id', 'in', self.session_ids.ids)]
            return action
        else:
            raise UserError(_("No Sessions to View."))


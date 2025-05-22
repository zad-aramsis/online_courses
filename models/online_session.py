from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class OnlineSession(models.Model):
    _name = 'online.session'
    _description = 'Online Course Session'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)
    name = fields.Char(string='Session Title', required=True, tracking=True)
    course_id = fields.Many2one('online.course', string='Course', required=True, ondelete='cascade', tracking=True)
    instructor_id = fields.Many2one('online.instructor', string='Instructor', required=True, tracking=True)
    start_datetime = fields.Datetime(string='Start Time', required=True, tracking=True)
    duration = fields.Float(string='Duration (Hours)', default=3.0, tracking=True)
    end_datetime = fields.Datetime(string='End Time', compute='_compute_end_datetime', store=True, tracking=True)
    seats = fields.Integer(string='Number of Attendee Seats', related='course_id.total_students', tracking=True)
    student_ids_domain = fields.Many2many('online.student', related='course_id.student_ids', string='Students')
    attendee_ids = fields.Many2many('online.student', 'session_student_attend_rel', 'session_id', 'student_id',
                                    string='Attendees')
    taken_seats = fields.Float(compute='_compute_taken_seats', string='Taken Seats (%)', store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)

    @api.depends('start_datetime', 'duration')
    def _compute_end_datetime(self):
        for session in self:
            if session.start_datetime and session.duration > 0:
                session.end_datetime = fields.Datetime.add(session.start_datetime, hours=session.duration)
            else:
                session.end_datetime = session.start_datetime

    @api.depends('seats', 'attendee_ids')
    def _compute_taken_seats(self):
        for session in self:
            if session.seats > 0:
                session.taken_seats = (len(session.attendee_ids) * 100.0) / session.seats
            else:
                session.taken_seats = 0.0

    @api.constrains('instructor_id', 'attendee_ids')
    def _check_instructor_not_in_attendees(self):
        for r in self:
            if r.instructor_id and r.instructor_id.partner_id and r.instructor_id.partner_id in r.attendee_ids.mapped('partner_id'):
                raise ValidationError(_("A session's instructor (partner) can't be an attendee of the same session."))

    def action_confirm(self):
        for session in self:
            session.state = 'confirmed'

    def action_mark_done(self):
        for session in self:
            if not self.attendee_ids:
                raise ValidationError(_("Attendees are required to Mark Session Done."))
            session.state = 'done'

    def action_cancel(self):
        for session in self:
            session.state = 'cancelled'

    def action_reset_to_draft(self):
        for session in self:
            if session.course_id.state == 'completed' :
                raise ValidationError(_("You cannot reset this session to draft because the course '%s' has already been completed.") % self.course_id.name)
            else:
                session.state = 'draft'

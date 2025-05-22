from odoo import models, fields, api
from odoo.exceptions import ValidationError


class OnlineInstructor(models.Model):
    _name = 'online.instructor'
    _description = 'Course Instructor'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _inherits = {'res.partner': 'partner_id'}
    _order = 'name'

    partner_id = fields.Many2one('res.partner', string='Contact Information',
                                 required=True, ondelete='restrict', auto_join=True)

    job_title = fields.Char()
    biography = fields.Html(string='Biography')

    expertise_tags_ids = fields.Many2many('instructor.expertise.tag', 'instructor_expertise_custom_tag_rel',
                                          'instructor_id', 'tag_id', string='Expertise Areas')

    course_ids = fields.Many2many('online.course', 'online_course_instructor_rel',
                                  'instructor_id', 'course_id', string='Courses Taught')
    session_ids = fields.One2many('online.session', 'instructor_id', string='Sessions Delivered')

    # _sql_constraints = [
    #     ('partner_uniq', 'unique (partner_id)', 'Each partner can only be linked to one instructor record.'),
    # ]

    @api.model
    def create(self, vals_list):
        instructors = super().create(vals_list)
        for instructor in self:
            if instructor.partner_id:
                instructor.partner_id.is_instructor = True
        return instructors

    def unlink(self):
        for instructor in self:
            if instructor.partner_id:
                instructor.partner_id.is_instructor = False
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


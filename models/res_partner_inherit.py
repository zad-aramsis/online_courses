
from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_instructor = fields.Boolean(string="Is an Instructor", default=False, tracking=True)
    is_student = fields.Boolean(string="Is a Student", default=False, tracking=True)

    instructor_profile_ids = fields.One2many('online.instructor', 'partner_id', string="Instructor Profiles")
    student_profile_ids = fields.One2many('online.student', 'partner_id', string="Student Profiles")

    def action_view_instructor_profile(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('online_courses.action_online_instructor_list')

        if len(self.instructor_profile_ids) == 1:
            action['views'] = [(self.env.ref('online_courses.view_online_instructor_form').id, 'form')]
            action['res_id'] = self.instructor_profile_ids.id
            action['context'] = {'create': False}
        else:
            action['domain'] = [('id', 'in', self.instructor_profile_ids.ids)]
            if not self.instructor_profile_ids and self.is_instructor:
                 action['context'] = {'default_partner_id': self.id, 'create': True}
            elif not self.instructor_profile_ids:
                action['context'] = {'default_partner_id': self.id, 'default_name': self.name, 'create': True}
                action['domain'] = [('partner_id', '=', self.id)]
        return action

    def action_view_student_profile(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('online_courses.action_online_student_list')
        if len(self.student_profile_ids) == 1:
            action['views'] = [(self.env.ref('online_courses.view_online_student_form').id, 'form')]
            action['res_id'] = self.student_profile_ids.id
            action['context'] = {'create': False}
        else:
            action['domain'] = [('id', 'in', self.student_profile_ids.ids)]
            if not self.student_profile_ids and self.is_student:
                action['context'] = {'default_partner_id': self.id, 'create': True}
            elif not self.student_profile_ids:
                action['context'] = {'default_partner_id': self.id, 'default_name': self.name, 'create': True}
                action['domain'] = [('partner_id', '=', self.id)]
        return action
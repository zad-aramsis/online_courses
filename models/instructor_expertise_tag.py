from odoo import models, fields


class InstructorExpertiseTag(models.Model):
    _name = 'instructor.expertise.tag'
    _description = 'Instructor Expertise Tag'
    _order = 'name'

    name = fields.Char(string='Name', required=True, translate=True)
    color = fields.Integer(string='Color Index', help="Color to be used for this tag in the interface.")
    active = fields.Boolean(default=True, help="Set active to false to hide the tag without removing it.")

    # _sql_constraints = [
    #     ('name_uniq', 'unique (name)', "Tag name must be unique!"),
    # ]

    instructor_count = fields.Integer(string="Instructors", compute='_compute_instructor_count')

    def _compute_instructor_count(self):
        instructor_data = self.env['online.instructor'].read_group(
            [('expertise_tags_ids', 'in', self.ids)],
            ['expertise_tags_ids'],
            ['expertise_tags_ids'])
        mapped_data = {data['expertise_tags_ids'][0]: data['expertise_tags_ids_count'] for data in instructor_data}
        for tag in self:
            tag.instructor_count = mapped_data.get(tag.id, 0)

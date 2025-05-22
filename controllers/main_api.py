from odoo import http
from odoo.http import request

class OnlineCoursesWebsite(http.Controller):

    @http.route('/online_courses/instructors', type='json', auth='public', website=True)
    def get_instructors(self):
        instructors = request.env['online.instructor'].sudo().search([], limit=6)
        if not instructors:
            return []
        return [{
            'id': inst.id,
            'name': inst.name,
            'job_title': inst.job_title,
            'image': f"/web/image/online.instructor/{inst.id}/image_1920"
        } for inst in instructors]

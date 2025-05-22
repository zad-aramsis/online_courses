{
    'name': "Online Courses",
    'summary': """
            Manage online courses, sessions, instructors, and students.
    """,
    'description': """
                  This module allows for the comprehensive management of online educational content,
                  including course creation, session scheduling, instructor and student registration,
                  and certification.
                  """,
    'author': "Abanob Ashraf/Zad Solutions",
    'website': "http://zadsolutions.com",
    'category': 'Education',
    'version': '17.0.1.0.0',
    'depends': ['base', 'mail', 'calendar', 'contacts'],
    'data': [
        # Security
        'security/security_groups.xml',
        'security/ir.model.access.csv',
        'security/record_rules.xml',

        # Data
        'data/cron_jobs.xml',
        'data/sequences.xml',
        'data/mail_templates.xml',

        # Reports
        'reports/certification_report.xml',
        'reports/certification_templates.xml',

        # Wizards
        'wizards/print_course_certificate_wizard_views.xml',

        # Views
        'views/res_partner_view_inherit.xml',
        'views/instructor_expertise_tag_views.xml',
        'views/online_course_views.xml',
        'views/online_session_views.xml',
        'views/online_instructor_views.xml',
        'views/online_student_views.xml',
        'views/actions.xml',
        'views/menu_items.xml',

    ],
    'assets': {
        'web.assets_backend': [
            'online_courses/static/src/js/about_us_action.js',
            'online_courses/static/src/css/about_us_style.css',
            'online_courses/static/src/xml/about_us_templates.xml',
        ],
    },
    'demo': ['demo/demo_data.xml'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

{
    'name': "Mindlab",

    'summary': "Mindlab",

    'description': """
Mindlab
    """,
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','openeducat_core','openeducat_parent','openeducat_admission','account','openeducat_attendance','nursery_rubric'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/op_course_views.xml',
        'views/op_student_views.xml',
        'views/op_academic_year.xml',
        'views/op_parent_views.xml',
        'views/op_admission_views.xml',
        'views/account_move_views.xml',
        'views/program_details_views.xml',
        'views/kit_type_views.xml',
        'views/kit_level_views.xml',
        'views/project_program_views.xml',
        'views/op_attendance_sheet_views.xml',
        'reports/assessment_report.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}



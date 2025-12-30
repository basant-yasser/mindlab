{
    "name": "Nursery Rubric + OpenEduCat Bridge",
    "version": "19.0.1.3.0",
    "category": "Education",
    "summary": "Course-based rubrics, assessments on student screen, and professional rubric PDF (OpenEduCat).",
    "depends": [
        "nursery_rubric",
        "openeducat_core"
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/op_course_inherit.xml",
        "views/assessment_inherit.xml",
        "report/report_inherit.xml"
    ],
    # "post_init_hook": "post_init_hook",
    "application": False,
    "license": "LGPL-3"
}

from odoo import api, SUPERUSER_ID

# def post_init_hook(cr, registry):
#     env = api.Environment(cr, SUPERUSER_ID, {})
#
#     base_view = env["ir.ui.view"].search(
#         [("model", "=", "op.student"), ("type", "=", "form")],
#         order="priority asc, id asc",
#         limit=1,
#     )
#     if not base_view:
#         return
#
#     name = "op.student.form.inherit.nursery_rubric.buttons_tab"
#     existing = env["ir.ui.view"].search([
#         ("name", "=", name),
#         ("type", "=", "form"),
#         ("inherit_id", "=", base_view.id),
#     ], limit=1)
#     if existing:
#         return
#
#     arch = '''
#     <data>
#       <xpath expr="//div[contains(@class,'oe_button_box')]" position="inside">
#         <button type="object" name="action_view_assessments" class="oe_stat_button" icon="fa-check-square-o">
#           <field name="assessment_ids" string="Assessments" widget="statinfo"/>
#         </button>
#
#         <button type="object" name="action_print_latest_assessment" class="oe_stat_button" icon="fa-print">
#           <div class="o_stat_info">
#             <span class="o_stat_text">Print Rubric</span>
#           </div>
#         </button>
#       </xpath>
#
#       <xpath expr="//notebook" position="inside">
#         <page string="Assessments">
#           <field name="assessment_ids" context="{'default_op_student_id': active_id}">
#             <tree>
#               <field name="date"/>
#               <field name="course_id"/>
#               <field name="rubric_id"/>
#               <field name="total_score"/>
#               <field name="performance_level"/>
#               <field name="state"/>
#             </tree>
#           </field>
#         </page>
#       </xpath>
#     </data>
#     '''
#     env["ir.ui.view"].create({
#         "name": name,
#         "type": "form",
#         "model": "op.student",
#         "inherit_id": base_view.id,
#         "arch_db": arch,
#     })

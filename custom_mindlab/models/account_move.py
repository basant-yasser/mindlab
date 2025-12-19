from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    register_id = fields.Many2one('op.admission.register', string='Admission Register')
    op_admission_id = fields.Many2one('op.admission', string='Op Admission')

    def action_view_admission_register(self):
        self.ensure_one()

        action = self.env["ir.actions.actions"]._for_xml_id(
            "openeducat_admission.act_open_op_admission_view"
        )

        action['domain'] = [
            ('id', '=', self.op_admission_id.id),
        ]

        return action


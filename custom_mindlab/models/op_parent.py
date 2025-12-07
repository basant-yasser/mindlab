from odoo import models, fields, api


class OpParent(models.Model):
    _inherit = 'op.parent'

    def action_view_partner_invoices(self):
        self.ensure_one()

        action = self.env["ir.actions.actions"]._for_xml_id(
            "account.action_move_out_invoice_type"
        )

        # Get the linked res.partner of this parent
        partner = self.name

        action['domain'] = [
            ('move_type', 'in', ('out_invoice', 'out_refund')),
            ('partner_id', '=', partner.id),
        ]

        action['context'] = {
            'default_move_type': 'out_invoice',
            'move_type': 'out_invoice',
            'journal_type': 'sale',
            'search_default_unpaid': 1
        }

        return action

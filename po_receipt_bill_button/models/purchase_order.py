from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    show_create_bill_button = fields.Boolean(compute='_compute_bill_credit_buttons')
    show_create_credit_note_button = fields.Boolean(compute='_compute_bill_credit_buttons')

    @api.depends('state', 'invoice_status', 'order_line.qty_to_invoice')
    def _compute_bill_credit_buttons(self):
        for order in self:
            qty_to_invoice_total = sum(order.order_line.mapped('qty_to_invoice'))
            can_create = order.state in ('purchase', 'done') and order.invoice_status == 'to invoice'
            order.show_create_bill_button = can_create and qty_to_invoice_total > 0
            order.show_create_credit_note_button = can_create and qty_to_invoice_total < 0

    def action_create_bill_or_credit_note(self):
        return self.action_create_invoice()

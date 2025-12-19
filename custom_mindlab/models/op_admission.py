from odoo import models, fields, api,_
from odoo.exceptions import UserError


class OpAdmission(models.Model):
    _inherit = 'op.admission'

    state = fields.Selection(
        selection_add=[
            ('waiting_invoice', 'Waiting Invoice'),
            ('done', ),
        ],
    )

    fees_start_date = fields.Date('Fees Start Date',required=True)

    def ready_to_invoice(self):
        self.state = 'waiting_invoice'

    def create_invoice(self):
        # self.state = 'done'
        invoice = self.env['account.move'].create({
            'op_admission_id': self.id,
            'move_type': 'out_invoice',
            'invoice_date': self.fees_start_date,
            'partner_id': self.partner_id.id if self.partner_id else False,
            'register_id': self.register_id.id if self.register_id else False,
            'invoice_line_ids': [(0, 0, {
                'product_id':self.register_id.product_id.id ,
                'price_unit': self.fees,
            })]
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Customer Invoice',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': invoice.id,
            'target': 'current',  # open in same window
        }

    def enroll_student(self):
        res = super().enroll_student()

        invoices = self.env['account.move'].search([
            ('op_admission_id', '=', self.id),
            ('move_type', '=', 'out_invoice'),
        ])

        if not invoices:
            raise UserError(_('No invoice found for this admission register.'))

        if any(inv.state != 'posted' for inv in invoices):
            raise UserError(_('Please post the invoice before enrollment.'))

        return res

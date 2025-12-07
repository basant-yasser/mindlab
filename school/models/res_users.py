# See LICENSE file for full copyright and licensing details.

from odoo import api, models


class ResUsers(models.Model):

    _inherit = "res.users"

    @api.model
    def create(self, vals):
        """Inherit method to create user of group teacher or parent."""

        # Handle single or multiple records
        vals_list = vals if isinstance(vals, list) else [vals]

        # Prepare values for each dict in the create batch
        for v in vals_list:
            v.update({"employee_ids": False})

        # Create users
        res = super(ResUsers, self).create(vals)

        # Post-creation actions (only works on recordsets)
        if self._context.get("teacher_create", False):
            teacher_group_ids = [
                self.env.ref("school.group_school_teacher").id,
                self.env.ref("base.group_user").id,
                self.env.ref("base.group_partner_manager").id,
            ]
            res.write(
                {
                    "groups_id": [(6, 0, teacher_group_ids)],
                    "company_id": self._context.get("school_id"),
                    "company_ids": [(4, self._context.get("school_id"))],
                }
            )

        return res


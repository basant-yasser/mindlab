# -*- coding: utf-8 -*-
###############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Anjana P V(odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
import base64
from odoo import http
from odoo.http import request
from datetime import datetime
import json

def _safe_datetime(value):
    if not value:
        return False
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M")
    except Exception as e:
        return False


class OnlineAdmission(http.Controller):
    """Controller for taking online admission"""

    @http.route('/admission/form/submit', type='http', auth="public",
                website=True, csrf=True)
    def eadm_submit(self, **kwargs):
        guardian = request.env['res.partner'].sudo().create({
                        'name': kwargs.get('middle_name'),
                        'is_parent': True
                    })

        binary_image = base64.b64encode((kwargs.get('image')).read())
        application = request.env['op.admission'].sudo().create({
            'name': kwargs.get('name'),
            'first_name': kwargs.get('name'),
            'middle_name': kwargs.get('middle_name'),
            'last_name': kwargs.get('last_name'),
            # 'mother_name': kwargs.get('mother'),
            # 'father_name': kwargs.get('father'),
            'phone': kwargs.get('phone'),
            'email': kwargs.get('email'),
            'birth_date': kwargs.get('birth_date'),
            'register_id': kwargs.get('admission_register'),
            'application_date':  _safe_datetime(kwargs.get('application_date')) or datetime.now(),
            # 'mother_tongue': kwargs.get('tongue'),
            # 'medium_id': kwargs.get('medium'),
            # 'sec_lang_id': kwargs.get('sec_lang'),
            'course_id': kwargs.get('courses'),
            'batch_id': kwargs.get('batches'),
            'title': kwargs.get('titles'),
            'fees_term_id': kwargs.get('fees_terms'),
            'partner_id': kwargs.get('partners'),
            'street': kwargs.get('street'),
            # 'per_street': kwargs.get('communication_address'),
            # 'blood_group': kwargs.get('blood_group'),
            'gender': kwargs.get('gender'),
            # 'guardian_id': guardian.id,
            'image': binary_image,
            'discount': kwargs.get('discount') if kwargs.get('discount') else 0,
            'fees': kwargs.get('fees') if kwargs.get('fees') else 0,
            'due_date': kwargs.get('due_date') if kwargs.get('due_date') else datetime.now(),
            'fees_start_date': kwargs.get('fees_start_date') if kwargs.get('fees_start_date') else datetime.now(),
            'admission_date': kwargs.get('admission_date') if kwargs.get('admission_date') else datetime.now(),
            'is_student' : bool(kwargs.get('is_student')) if kwargs.get('is_student') else False,
            'company_id': request.env.company.id,
        })
        # attachment = request.env['ir.attachment'].sudo().create({
        #     'name': kwargs.get('document_attachment').filename,
        #     'type': 'binary',
        #     'datas': base64.b64encode(
        #         (kwargs.get('document_attachment')).read()),
        # })
        # request.env['education.document'].sudo().create({
        #     'application_ref_id': application.id,
        #     'document_type_id': kwargs.get('doc_type'),
        #     'doc_attachment_ids': [(4, attachment.id)],
        # })
        return request.render(
            "education_student_portal.submit_admission", {})

    @http.route('/online_admission', type='http', auth='public', website=True)
    def online_admission(self):
        """To pass certain default field values to the website registration
        form."""

        vals = {
            # 'class': request.env['education.class'].sudo().search([]),
            # 'year': request.env['education.academic.year'].sudo().search([]),
            'courses': request.env['op.course'].sudo().search([]),
            'batch': request.env['op.batch'].sudo().search([]),
            'fees_term': request.env['op.fees.terms'].sudo().search([]),
            'year': request.env['op.admission.register'].sudo().search([('state', 'in', ['application', 'admission'])]),
            'medium': request.env['education.medium'].sudo().search([]),
            # 'sec_lang': request.env['education.subject'].sudo().search([]),
            # 'doc_type': request.env['document.document'].sudo().search([]),
            'partner': request.env['res.partner'].sudo().search([]),
            'title': request.env['res.partner.title'].sudo().search([])

        }
        return request.render('education_student_portal.online_admission', vals)

    @http.route('/get_courses_by_admission/<int:admin_id>', type='http', auth='user')
    def get_lots_by_product(self, admin_id, **kw):
        courses = request.env['op.admission.register'].sudo().search([('id', '=', admin_id)])
        data = [{'id': course.course_id.id, 'name': course.course_id.name} for course in courses]
        return request.make_response(
            json.dumps(data),
            headers=[('Content-Type', 'application/json')]
        )


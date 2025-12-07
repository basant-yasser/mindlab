# from odoo import http


# class CustomMindlab(http.Controller):
#     @http.route('/custom_mindlab/custom_mindlab', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/custom_mindlab/custom_mindlab/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('custom_mindlab.listing', {
#             'root': '/custom_mindlab/custom_mindlab',
#             'objects': http.request.env['custom_mindlab.custom_mindlab'].search([]),
#         })

#     @http.route('/custom_mindlab/custom_mindlab/objects/<model("custom_mindlab.custom_mindlab"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('custom_mindlab.object', {
#             'object': obj
#         })


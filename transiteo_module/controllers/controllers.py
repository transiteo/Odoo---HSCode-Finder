# -*- coding: utf-8 -*-
# from odoo import http


# class Transiteo(http.Controller):
#     @http.route('/transiteo/transiteo', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/transiteo/transiteo/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('transiteo.listing', {
#             'root': '/transiteo/transiteo',
#             'objects': http.request.env['transiteo.transiteo'].search([]),
#         })

#     @http.route('/transiteo/transiteo/objects/<model("transiteo.transiteo"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('transiteo.object', {
#             'object': obj
#         })

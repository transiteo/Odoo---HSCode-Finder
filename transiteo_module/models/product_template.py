# -*- coding: utf-8 -*-

# from odoo import models, fields, api
from odoo import models, fields, api
import requests
import json
from datetime import datetime, timedelta


# class transiteo(models.Model):
#     _name = 'transiteo.transiteo'
#     _description = 'transiteo.transiteo'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

class product_template(models.Model):
    _name = 'product.template'
    _inherit = 'product.template'

    name = fields.Char(string="Nom de l'article")
    id_token_name = fields.Many2one('auth.transiteo', 'Authentication')
    id_token_auth = fields.Char(related='id_token_name.id_token')
    from_country_name = fields.Many2one('res.country', "Country of shipment")
    from_country_alpha2 = fields.Char(related='from_country_name.code')
    to_country_name = fields.Many2one('res.country', 'Country of destination')
    to_country_alpha2 = fields.Char(related='to_country_name.code')
    #hs = fields.Char(string='HSCode', store=False, compute='_get_hs')
    hs_europe = fields.Char(string='European HSCode')
    hs_europe_stocked = fields.Char(string='European stored HSCode')
    hs = fields.Char(string='HSCode')
    taux_duties = fields.Float(string="Taux de droits de douane")
    duties_message = fields.Char(string="Taux de droits de douane")
    standard_price = fields.Float(string="Cost")
    cal_duties = fields.Float(string="Droits de douane calculés", compute='_calc_duties')
    # main_class_id = fields.Many2one('main.class', string="HSCodes")
    # to_country_tab = fields.Char(related='to_country_name.name')
    # hs_tab = fields.Char('HSCode')
    item_ids = fields.One2many('res.users.productitem', 'product_id')

    # Lui faire voir
    # item_ids = fields.One2many('product.template', 'product_id')
    # product_id = fields.Many2one('product.template')
    # item_id = fields.Many2one('product.template', 'Product Item')
    #
    # to_country_tab = fields.Char(string='Pays de destination')
    # hs_tab = fields.Char(string="HSCode")

    # def _get_hs(self):
    #     headers = {"Content-Type": "application/json",
    #                "Authorization": self.id_token_auth}
    #
    #     body = {
    #         "product": {
    #             "identification": {
    #                 "value": "Gateau pepito",
    #                 "type": "TEXT"
    #             }
    #         },
    #         "from_country": "MAR",
    #         "to_country": "FRA",
    #         "ai_score": True,
    #         "multi_results": 3
    #     }
    #
    #     temp_body = body.copy()
    #     temp_body["product"]["identification"]["value"] = self.name
    #     temp_body["to_country"] = self.to_country_alpha2
    #     r = requests.post("https://api.dev.transiteo.io/v1/taxsrv/hscodefinder", headers=headers,
    #                       data=json.dumps(temp_body))
    #     if 'message' in dict(r.json()):
    #         self.hs = r.json()['message']
    #     else:
    #         self.hs = r.json()[0]['result']['hs_code']

    #@api.onchange('name')
    #@api.depends('name')
    #@api.multi
    def _get_hs(self):
        self.synchronize_hscode_eu()
        # self.ensure_one()
        headers = {"Content-Type": "application/json",
                   #"Authorization": "eyJraWQiOiI4eXVTYUd5WHNEUCtIOTU0UjYxd1Z4QkMyNHUydzRUclF5NEZzd3BobDJNPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiIwMzU5NWM5Mi01MmUyLTQ1NDUtODQ4Ni02ZjE1NjJlYThmN2UiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiY3VzdG9tOmNvbXBhbnlfbmFtZSI6Ik15IGNvbXBhbnkiLCJjdXN0b206bGFuZyI6ImZyIiwiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLmV1LXdlc3QtMS5hbWF6b25hd3MuY29tXC9ldS13ZXN0LTFfRnBCZ3JuQjBpIiwicGhvbmVfbnVtYmVyX3ZlcmlmaWVkIjpmYWxzZSwiY29nbml0bzp1c2VybmFtZSI6IjAzNTk1YzkyLTUyZTItNDU0NS04NDg2LTZmMTU2MmVhOGY3ZSIsImF1ZCI6IjI0bDhsdGRodnFyZDU3Z2dnNG4zNG1yc250IiwiZXZlbnRfaWQiOiIzMzM4Nzc4Yy0wODgwLTQxNGUtOTBiOS00NDk4NjA5MDk4OWYiLCJ0b2tlbl91c2UiOiJpZCIsImN1c3RvbTpjdXJyZW5jeSI6ImV1ciIsImF1dGhfdGltZSI6MTY1NjU5NTk1MywibmFtZSI6Ik1vaGFtbWVkIiwicGhvbmVfbnVtYmVyIjoiKzMzNjAwMDAwMDAwIiwiZXhwIjoxNjYzMTYzMjU3LCJpYXQiOjE2NjMwNzY4NTcsImZhbWlseV9uYW1lIjoiQmVsaGFqIiwiZW1haWwiOiJtb2hhbW1lZCtkZXZhcGlAdHJhbnNpdGVvLmNvbSJ9.nQiRTdMkcTTwyuUyqzr3X-O61tPMoANzvwo2pYPiTWKUZuoGgXz1r2hIR9nPs55Qp3NXN9Rg2wTnKQ3tBVXjYTQsis5n9x85_78Ve6BnRTNUQQagy2y0uSxwZ-Ql8CVSZ-4CRIkLrOXcbhhOTtuFCq5i7wWIm13w-LJVTtDMGB1ByuSycE0iBDRU0JJ8TEtX8BTOP0f48Ji0Y1y4-9XthxZ0NxTeqspJaI_630a3_yGqNnTgnEe6brkLCXWJE9MCwI8BAFrHPZY1Gft5UlDzLw8XNyNu3-ZI_N91lWzkwchN_TE7_vDbcxC1cXe1Tdp3tgT-HaidBUaARmGshdijqw"}
                   "Authorization": self.id_token_auth}

        if not self.id_token_auth:
        #if not True:QQ
            self.hs = ''
        else:
            body = {
                "product": {
                    "identification": {
                        "value": "8471607000",
                        "type": "HSCODE"
                    }
                },
                "from_country": "FRA",
                "to_country": "FRA",
                "ai_score": True,
                "multi_results": 3
            }

            temp_body = body.copy()
            temp_body["product"]["identification"]["value"] = self.hs_europe_stocked
            print(self.hs_europe)
            # temp_body["from_country"] = "FRA"
            temp_body["to_country"] = self.to_country_alpha2
            r = requests.post("https://api.dev.transiteo.io/v1/taxsrv/hscodefinder", headers=headers,
                              data=json.dumps(temp_body))
            if 'message' in dict(r.json()):
                #self.hs = 'aaaa'
                self.hs = r.json()['message']
            else:
                #self.hs = 'bbbb'
                self.hs = r.json()['result']['hs_code']

    #             body1 = {
    #                 "hs_code": "4202310000",
    #                 "from_country": "FRA",
    #                 "to_country": "VEN"
    #             }
    #             temp_body1 = body1.copy()
    #             temp_body1["hs_code"] = self.hs
    #             temp_body1["from_country"] = self.from_country_alpha2
    #             temp_body1["to_country"] = self.to_country_alpha2
    #             re = requests.post("https://api.dev.transiteo.io/v1/data/duties", headers=headers,
    #                                data=json.dumps(temp_body1))
    #             if 'message' in dict(re.json()):
    #                 self.duties_message = re.json()['message']
    #             else:
    #                 self.taux_duties = re.json()['tariff_ave']
    #
    # def _calc_duties(self):
    #     self.cal_duties = self.standard_price + (self.standard_price * self.taux_duties)

    def search_hs(self):
        self._get_hs()

    def synchronize_hscode_eu(self):
        self.hs_europe_stocked = self.hs_europe

    # Lui faire voir
    # def synchronize(self):
    #     self.to_country_tab = self.to_country_alpha2
    #     self.hs_tab = self.hs
    #     print(self.to_country_tab + " & " + self.hs_tab)

    def _get_hs_europe(self):
        headers = {"Content-Type": "application/json",
                   "Authorization": self.id_token_auth}

        if not self.id_token_auth:
            self.hs_europe = ''
        else:
            body = {
                "product": {
                    "identification": {
                        "value": "Gateau pepito",
                        "type": "TEXT"
                    }
                },
                "to_country": "FRA",
                "ai_score": True,
                "multi_results": 3
            }

            temp_body = body.copy()
            temp_body["product"]["identification"]["value"] = self.name
            r = requests.post("https://api.dev.transiteo.io/v1/taxsrv/hscodefinder", headers=headers,
                              data=json.dumps(temp_body))
            if 'message' in dict(r.json()):
                self.hs_europe = r.json()['message']
            else:
                self.hs_europe = r.json()[0]['result']['hs_code']

    def search_hs_europe(self):
        self._get_hs_europe()

    # def _get_duties(self):
    #     headers = {"Content-Type": "application/json",
    #                "Authorization": self.id_token_auth}
    #
    #     if not self.id_token_auth:
    #         self.hs = ''
    #
    #     body = {
    #         "hs_code": "4202310000",
    #         "from_country": "FRA",
    #         "to_country": "VEN"
    #     }
    #
    #     temp_body = body.copy()
    #     temp_body["hs_code"] = self.hs
    #     if self.hs == '':
    #         self.taux_duties = 0.0
    #     else:
    #         temp_body["from_country"] = self.from_country_alpha2
    #         temp_body["to_country"] = self.to_country_alpha2
    #         r = requests.post("https://api.dev.transiteo.io/v1/data/duties", headers=headers,
    #                           data=json.dumps(temp_body))
    #
    #         if 'message' in dict(r.json()):
    #             self.taux_duties = r.json()['message']
    #         else:
    #             self.taux_duties = r.json()['tariff_ave']

# class product_relation(models.Model):
#     _name = 'product.template'
#     _inherit = 'product.template'
#
#     one2many_hs = fields.One2many('product.template', 'to_country_name', string="Details")

# class Mainclass(models.Model):
#     _name = 'product.template'
#     _inherit = 'product.template'
#
#     notebook_ids = fields.One2many('product.template', 'main_class_id', string="Autres pays")

# class DietFacts_res_users_meal(models.Model):
#     _name = 'res.users.product'
#     item_ids = fields.One2many('res.users.productitem', 'product_id')

class DietFacts_res_users_mealitem(models.Model):
    _name = 'res.users.productitem'

    product_id = fields.Many2one('product.template')
    item_id = fields.Many2one('product.template', 'Product Item')
    # to_country_tab = fields.Char(related='item_id.to_country_name.name', string="Pays de destination", store=True, readonly=True)
    # hs_tab = fields.Char(related='item_id.hs', string="HSCode", store=True, readonly=True)
    # to_country_tab = fields.Char(string="Pays de destination")
    to_country_tab = fields.Many2one('res.country', 'Country of destination')
    hs_tab = fields.Char(string="HSCode")


# access_res_users_productitem,res.users.productitem,model_res_users_productitem,,1,1,1,1

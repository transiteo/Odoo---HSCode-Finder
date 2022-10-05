# -*- coding: utf-8 -*-

# from odoo import models, fields, api
from odoo import models, fields, api
import requests
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

class Authentification(models.Model):
    _name = "auth.transiteo"

    name = fields.Char(string='Name')
    client_id = fields.Char(string="Client ID")
    refresh_token = fields.Char(string="Refresh Token")
    id_token = fields.Char(string='ID Token', compute='get_id_token')
    #date_exp = fields.Char(string="Date d'expiration de la session", compute='_getdate')
    date_exp = fields.Char(string="Session expiration date")

    @api.onchange('client_id', 'refresh_token')
    def get_id_token(self):
        RT = self.refresh_token
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        body = {
            "grant_type": "refresh_token",
            "refresh_token": RT,
            "client_id": self.client_id
        }
        r = requests.post("https://auth.dev.transiteo.io/oauth2/token", headers=headers, data=body)
        #self.id_token = r.json()['id_token']
        last_hour_date_time = datetime.now() + timedelta(hours=26)
        if 'id_token' not in dict(r.json()):
            self.id_token = r.json()['error']
            self.date_exp = "There is no expiration date because the session is invalid"
        else:
            self.id_token = r.json()['id_token']
            self.date_exp = last_hour_date_time.strftime('%Y-%m-%d %H:%M:%S')

    # @api.onchange('id_token')
    # def _getdate(self):
    #     last_hour_date_time = datetime.now() + timedelta(hours=26)
    #     self.date_exp = last_hour_date_time.strftime('%Y-%m-%d %H:%M:%S')
# -*- coding: utf-8 -*-

import logging
from datetime import datetime, date, timedelta

from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    account_ref_id = fields.Many2one('account.account', string="Cuenta Referencia")

    @api.onchange('account_ref_id')
    def onchange_account_primary_id(self):
        l_acc = []
        for acc in self.account_ref_id:
            l_acc.append(int(acc[0]))
        return {'domain': {'account_id': [('account_id', 'in', l_acc)]}}

class AccountAccount(models.Model):
    _inherit = 'account.account'

    account_id = fields.Many2one('account.account', string="Cuenta padre")
    activity = fields.Selection([('Op','Operación'),
                                ('In','Inversión'),
                                ('FI','Financiamiento')], string="Actividad", required=True)

    @api.onchange('account_id')
    def onchange_account_id(self):
        account_ids = self.env['account.account'].search([('account_id','=',self.account_id.id)])
        num = len(account_ids) + 1
        if self.account_id:
            self.code = self.account_id.code + "." + str(num)

class AccountEcuationMove(models.Model):
    _name = 'account.ecuation.move'

    name = fields.Char(string="Nombre")
    ref = fields.Char(string="Referencia")
    journal_id = fields.Many2one('account.journal', string="Diario", required=True)
    line_ids = fields.One2many('account.ecuation.line', 'ecuation_id', string="Apuntes contables")

    def get_account_move(self):
        for record in self:
            xline = []
            for line in record.line_ids:
                move_ids = {
                            'account_id': line.account_id.id,
                            'partner_id': line.partner_id.id,
                            'name': line.name,
                            'debit': line.debit,
                            'credit': line.credit,
                }
                xline.append(move_ids)
            print("################# SELF XLINE >>>>>>>>>>>>>> ", xline)
            return {
                'name'          :   'Apuntes contables',
                'type'          :   'ir.actions.act_window',
                'view_type'     :   'form',
                'view_mode'     :   'form',
                'target'        :   'current', 
                'context'       :  {'default_ref': record.ref,
                                    'default_journal_id': record.journal_id.id,
                                    'default_line_ids': xline,},
                'res_model'     :   'account.move',
            }

class AccountEcuationLine(models.Model):
    _name = 'account.ecuation.line'

    ecuation_id = fields.Many2one('account.ecuation.move', string="Ref ecuación")
    account_primary_id = fields.Many2one('account.account', string="Cuenta primaria", domain="[('account_id','=',False)]")
    account_id = fields.Many2one('account.account', string="Cuenta")
    partner_id = fields.Many2one('res.partner', string="Empresa")
    name = fields.Char(string="Descripción")
    debit = fields.Float(string="Debe")
    credit = fields.Float(string="Haber")

    @api.onchange('account_primary_id')
    def onchange_account_primary_id(self):
        l_acc = []
        for acc in self.account_primary_id:
            l_acc.append(int(acc[0]))
        return {'domain': {'account_id': [('account_id', 'in', l_acc)]}}

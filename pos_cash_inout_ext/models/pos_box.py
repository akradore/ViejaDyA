# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

from openerp import models, fields, api, _
from odoo.addons.account.wizard.pos_box import CashBox


class PosConfig(models.Model):
    _inherit = 'pos.config'

    print_receipt = fields.Boolean("Print Receipt")
    enable_cash_in_out = fields.Boolean("Cash In Out")


class res_users(models.Model):
    _inherit = 'res.users'

    print_cash_statement = fields.Boolean('Print Cash In-Out Statement')


class pos_session(models.Model):
    _inherit = 'pos.session'

    @api.model
    def cash_in_out_operation(self, vals):
        cash_obj = False
        if vals:
            if vals.get('operation') == "put_money":
                cash_obj = self.env['cash.box.in']
            elif vals.get('operation') == "take_money":
                cash_obj = self.env['cash.box.out']
        session_id = self.env['pos.session'].browse(vals.get('session_id'))
        if session_id:
            for session in session_id:
                bank_statements = [session.cash_register_id for session in session_id if session.cash_register_id]
            if not bank_statements:
                return  {'error': _('There is no cash register for this PoS Session')}
            cntx = {'active_id':session_id.id,'uid':vals.get('cashier')}
            res = cash_obj.with_context(cntx).create({'name': vals.get('name'), 'amount': vals.get('amount')})
            return res._run(bank_statements)
        return {'error': _('There is no cash register for this PoS Session')}


class cash_in_out_history(models.Model):
    _name = 'cash.in.out.history'

    user_id = fields.Many2one('res.users', string='User ID')
    session_id = fields.Many2one('pos.session', String="Session ID")
    amount = fields.Float("Amount")
    operation = fields.Selection([('Dr', 'Dr'), ('Cr', 'Cr')], string="Operation")


# Put money in from backend
class PosBoxIn(CashBox):
    _inherit = 'cash.box.in'

    @api.model
    def create(self, vals):
        res = super(PosBoxIn, self).create(vals)
        cash_out_obj_history = self.env['cash.in.out.history']
        if res and self._context:
            user_id = self._context.get('uid')
            session_record_id = self._context.get('active_id')
            history_val = {'user_id': user_id, 'session_id': session_record_id, 'amount': vals.get('amount'),
                           'operation': 'Cr'}
            cash_out_obj_history.create(history_val)
        return res

# Take money out from backend
class PosBoxOut(CashBox):
    _inherit = 'cash.box.out'

    @api.model
    def create(self, vals):
        res = super(PosBoxOut, self).create(vals)
        cash_out_obj_history = self.env['cash.in.out.history']
        if res and self._context:
            user_id = self._context.get('uid')
            session_record_id = self._context.get('active_id')
            history_val = {'user_id': user_id, 'session_id': session_record_id, 'amount': vals.get('amount'),
                           'operation': 'Dr'}
            cash_out_obj_history.create(history_val)
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
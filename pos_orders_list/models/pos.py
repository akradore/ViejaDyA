# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from odoo.exceptions import Warning
import random
from datetime import date, datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import logging
_logger = logging.getLogger(__name__)
try:
	import barcode
except ImportError :
	_logger.debug('Cannot `import barcode` please run this command: sudo pip3 install python-barcode')

try:            
	from barcode.writer import ImageWriter
except ImportError:
	ImageWriter = None

import base64
import os
from functools import partial




class pos_order(models.Model):
	_inherit = 'pos.order'

	pos_order_date = fields.Date('Oder Date', compute='get_order_date')
	barcode = fields.Char(string="Order Barcode")
	barcode_img = fields.Binary('Order Barcode Image')

	@api.multi
	def get_order_date(self):
		for i in self:
			d1= datetime.strptime(i.date_order,DEFAULT_SERVER_DATETIME_FORMAT).date()
			i.pos_order_date = d1

	
	def return_new_order(self):
		lines = []
		for ln in self.lines:
			lines.append(ln.id)
		vals = {
			'amount_total': self.amount_total,
			'date_order': self.date_order,
			'id': self.id,
			'name': self.name,
			'partner_id': [self.partner_id.id, self.partner_id.name],
			'pos_reference': self.pos_reference,
			'state': self.state,
			'session_id': [self.session_id.id, self.session_id.name],
			'company_id': [self.company_id.id, self.company_id.name],
			'lines': lines,
		}
		return vals
	
	def return_new_order_line(self):
	
		orderlines = self.env['pos.order.line'].search([('order_id.id','=', self.id)])
	
		final_lines = []
	
		for l in orderlines:
			vals1 = {
				'discount': l.discount,
				'id': l.id,
				'order_id': [l.order_id.id, l.order_id.name],
				'price_unit': l.price_unit,
				'product_id': [l.product_id.id, l.product_id.name],
				'qty': l.qty,
			}
			final_lines.append(vals1)
	
		return final_lines


	def get_barcode(self,brcd):
		code = (random.randrange(1111111111111,9999999999999))
		bcode = self.env['barcode.nomenclature'].sanitize_ean("%s" % (code))
		pos_order = self.env['pos.order'].search([])
		for i in pos_order:
			if i.barcode  == bcode:
				code = (random.randrange(1111111111111,9999999999999))
				bcode = self.env['barcode.nomenclature'].sanitize_ean("%s" % (code))
		if ImageWriter != None:
			encode = barcode.get('ean13', bcode, writer=ImageWriter())
			filename = encode.save('ean13')
			file = open(filename, 'rb')
			jpgdata = file.read()
			imgdata = base64.encodestring(jpgdata)
			os.remove(filename) 
			return [bcode,imgdata]

	@api.model
	def _order_fields(self, ui_order):
		process_line = partial(self.env['pos.order.line']._order_line_fields, session_id=ui_order['pos_session_id'])
		return {
			'name':         ui_order['name'],
			'user_id':      ui_order['user_id'] or False,
			'session_id':   ui_order['pos_session_id'],
			'lines':        [process_line(l) for l in ui_order['lines']] if ui_order['lines'] else False,
			'pos_reference': ui_order['name'],
			'partner_id':   ui_order['partner_id'] or False,
			'date_order':   ui_order['creation_date'],
			'fiscal_position_id': ui_order['fiscal_position_id'],
			'pricelist_id': ui_order['pricelist_id'],
			'amount_paid':  ui_order['amount_paid'],
			'amount_total':  ui_order['amount_total'],
			'amount_tax':  ui_order['amount_tax'],
			'amount_return':  ui_order['amount_return'],
			'barcode': ui_order['barcode'],
			'barcode_img': ui_order['barcode_img'],
		}

class pos_config(models.Model):
	_inherit = 'pos.config'
	
	show_order = fields.Boolean('Show Orders')
	pos_session_limit = fields.Selection([('all',  "Load all Session's Orders"), ('last3', "Load last 3 Session's Orders"), ('last5', " Load last 5 Session's Orders"),('current_day', "Only Current Day Orders"), ('current_session', "Only Current Session's Orders")], string='Session limit',default="current_day")
	show_barcode = fields.Boolean('Show Barcode in Receipt')
	show_draft = fields.Boolean('Show Draft Orders')
	show_posted = fields.Boolean('Show Posted Orders')


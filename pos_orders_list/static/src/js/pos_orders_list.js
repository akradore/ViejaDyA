// pos_orders_list js
//console.log("custom callleddddddddddddddddddddd")
odoo.define('pos_orders_list.pos_orders_list', function(require) {
	"use strict";

	var models = require('point_of_sale.models');
	var screens = require('point_of_sale.screens');
	var PosDB = require('point_of_sale.DB');
	var core = require('web.core');
	var gui = require('point_of_sale.gui');
	var popups = require('point_of_sale.popups');
	var QWeb = core.qweb;
	var rpc = require('web.rpc');
	var time = require('web.time');
	var field_utils = require('web.field_utils');
	var utils = require('web.utils');
	var round_pr = utils.round_precision;
	var session = require('web.session');


	var _t = core._t;
	var bcode;
	var bcode_img;
	var order_id1;


// Load Models here...

	models.load_models({
		model: 'pos.order',
		fields: ['name', 'id', 'date_order', 'partner_id', 'pos_reference', 'lines', 'amount_total', 'session_id', 'state', 'company_id','pos_order_date','barcode','barcode_img'],
		domain: function(self){ 
			var current = self.pos_session.id
			
			if (self.config.pos_session_limit == 'all')
			{
				if(self.config.show_draft == true)
				{
					if(self.config.show_posted == true)
					{
						return [['state', 'in', ['draft','done']]]; 
					}
					else{
						return [['state', 'in', ['draft']]]; 
					}
				}
				else if(self.config.show_posted == true)
				{
					return [['state', 'in', ['done']]];
				}
				else{
					return [['state', 'in', ['draft','done','paid','invoiced','cancel']]]; 
				}	
			}
			if (self.config.pos_session_limit == 'last3')
			{
				if(self.config.show_draft == true)
				{
					if(self.config.show_posted == true)
					{
						return [['state', 'in', ['draft','done']],['session_id', 'in',[current,current-1,current-2,current-3]]]; 
					}
					else{
						return [['state', 'in', ['draft']],['session_id', 'in',[current,current-1,current-2,current-3]]]; 
					}
				}
				else if(self.config.show_posted == true)
				{
					return [['state', 'in', ['done']],['session_id', 'in',[current,current-1,current-2,current-3]]];
				}
				else{
					return [['session_id', 'in',[current,current-1,current-2,current-3]]]; 
				}
			}
			if (self.config.pos_session_limit == 'last5')
			{
				if(self.config.show_draft == true)
				{
					if(self.config.show_posted == true)
					{
						return [['state', 'in', ['draft','done']],['session_id', 'in',[current,current-1,current-2,current-3,current-4,current-5]]]; 
					}
					else{
						return [['state', 'in', ['draft']],['session_id', 'in',[current,current-1,current-2,current-3,current-4,current-5]]]; 
					}
				}
				else if(self.config.show_posted == true)
				{
					return [['state', 'in', ['done']],['session_id', 'in',[current,current-1,current-2,current-3,current-4,current-5]]];
				}
				else{
					return [['session_id', 'in',[current,current-1,current-2,current-3,current-4,current-5]]]; 
				}
			}
			
			if (self.config.pos_session_limit == 'current_session')
			{
				if(self.config.show_draft == true)
				{
					if(self.config.show_posted == true)
					{
						return [['state', 'in', ['draft','done']],['session_id', 'in',[current]]]; 
					}
					else{
						return [['state', 'in', ['draft']],['session_id', 'in',[current]]]; 
					}
				}
				else if(self.config.show_posted == true)
				{
					return [['state', 'in', ['done']],['session_id', 'in',[current]]];
				}
				else{
					return [['session_id', 'in',[current]]]; 
				}
			}
			
		}, 
		loaded: function(self, orders){
			self.db.all_orders_list = [];
			var today = new Date();
			var dd = today.getDate();
			var mm = today.getMonth()+1; //January is 0!

			var yyyy = today.getFullYear();
			if(dd<10){
				dd='0'+dd;
			} 
			if(mm<10){
				mm='0'+mm;
			} 
			today = yyyy+'-'+mm+'-'+dd;
			if (self.config.pos_session_limit == 'current_day')
			{
				orders.forEach(function(i) {
					if(today == i.pos_order_date)
					{
						if(self.config.show_draft == true)
						{
							if(self.config.show_posted == true)
							{
								if(i.state == 'done' || i.state == 'draft' )
								{
									self.db.all_orders_list.push(i);
								}
							}
							else{
								if(i.state == 'draft')
								{
									self.db.all_orders_list.push(i);
								}
							}
						}
						else if(self.config.show_posted == true)
						{
							if(i.state == 'done')
							{
								self.db.all_orders_list.push(i);
							}
						}
						else{
							self.db.all_orders_list.push(i);
						}
					}
				});
			}
			else{
				self.db.all_orders_list = orders;
			}
			self.db.get_orders_by_id = {};
			orders.forEach(function(order) {
				self.db.get_orders_by_id[order.id] = order;
			});
			self.orders = orders;
		},
	});

	models.load_models({
		model: 'pos.order.line',
		fields: ['order_id', 'product_id', 'discount', 'qty', 'price_unit',],
		domain: function(self) {
			var order_lines = []
			var orders = self.db.all_orders_list;
			for (var i = 0; i < orders.length; i++) {
				order_lines = order_lines.concat(orders[i]['lines']);
			}
			return [['id', 'in', order_lines]];
		},
		loaded: function(self, pos_order_line) {
			self.db.all_orders_line_list = pos_order_line;
			self.db.get_lines_by_id = {};
			pos_order_line.forEach(function(line) {
				self.db.get_lines_by_id[line.id] = line;
			});

			self.pos_order_line = pos_order_line;
		},
	});

	var OrderSuper = models.Order;
	var posorder_super = models.Order.prototype;
	models.Order = models.Order.extend({
		initialize: function(attr, options) {
			posorder_super.initialize.call(this,attr,options);
			this.barcode = this.barcode || "";
			this.barcode_img = this.barcode_img || "";
			this.set_barcode();

		},

		set_barcode: function(){
			var self = this;
			rpc.query({
						model: 'pos.order',
						method: 'get_barcode',
						args: [1,this['uid']],
					}).then(function(output) {
						self.barcode = output[0];
						self.barcode_img = output[1];
				});
		},

		get_barcode_data: function(){
			var brcd = [this.barcode,this.barcode_img]
			return brcd;
		},

		export_as_JSON: function() {
			var self = this;
			var loaded = OrderSuper.prototype.export_as_JSON.call(this);
			loaded.barcode = self.barcode;
			loaded.barcode_img = self.barcode_img
			return loaded;
		},

	});

	var _super_posmodel = models.PosModel.prototype;
	models.PosModel = models.PosModel.extend({

		_save_to_server: function (orders, options) {
			if (!orders || !orders.length) {
				var result = $.Deferred();
				result.resolve([]);
				return result;
			}

			options = options || {};

			var self = this;
			var timeout = typeof options.timeout === 'number' ? options.timeout : 7500 * orders.length;
			var order_ids_to_sync = _.pluck(orders, 'id');
			var args = [_.map(orders, function (order) {
					order.to_invoice = options.to_invoice || false;
					return order;
				})];
			return rpc.query({
					model: 'pos.order',
					method: 'create_from_ui',
					args: args,
					kwargs: {context: session.user_context},
				}, {
					timeout: timeout,
					shadow: !options.to_invoice
				})
				.then(function (server_ids) {
					_.each(order_ids_to_sync, function (order_id) {
						self.db.remove_order(order_id);
					});
					self.set('failed',false);
					order_id1 = server_ids;
					var order = self.get_order();
					
					if(self.config.show_posted == true || self.config.show_draft == true ){
						return server_ids;
					}
					else{
						rpc.query({
							model: 'pos.order',
							method: 'return_new_order',
							args: [server_ids],
							
							}).then(function(output) {
								self.db.all_orders_list.unshift(output);
								self.db.get_orders_by_id[server_ids] = server_ids;
						});

						rpc.query({
							model: 'pos.order',
							method: 'return_new_order_line',
							args: [server_ids],
							
							}).then(function(output1) {
								for(var ln=0; ln < output1.length; ln++){
									self.db.all_orders_line_list.unshift(output1[ln]);
								}

						});
					}
				}).fail(function (type, error){
					if(error.code === 200 ){    // Business Logic Error, not a connection problem
						//if warning do not need to display traceback!!
						if (error.data.exception_type == 'warning') {
							delete error.data.debug;
						}

						// Hide error if already shown before ...
						if ((!self.get('failed') || options.show_error) && !options.to_invoice) {
							self.gui.show_popup('error-traceback',{
								'title': error.data.message,
								'body':  error.data.debug
							});
						}
						self.set('failed',error);
					}
					console.error('Failed to send orders:', orders);
				});
		},

	});

	// SeeAllOrdersScreenWidget start

	var SeeAllOrdersScreenWidget = screens.ScreenWidget.extend({
		template: 'SeeAllOrdersScreenWidget',
		init: function(parent, options) {
			this._super(parent, options);
			//this.options = {};
		},
		
		line_selects: function(event,$line,id){
			var self = this;
			var orders = this.pos.db.get_orders_by_id[id];
			this.$('.client-list .lowlight').removeClass('lowlight');
			if ( $line.hasClass('highlight') ){
				$line.removeClass('highlight');
				$line.addClass('lowlight');
				//this.display_orders_detail('hide',orders);
				//this.new_clients = null;
				//this.toggle_save_button();
			}else{
				this.$('.client-list .highlight').removeClass('highlight');
				$line.addClass('highlight');
				var y = event.pageY - $line.parent().offset().top;
				this.display_orders_detail('show',orders,y);
				//this.new_clients = orders;
				//this.toggle_save_button();
			}
			
		},
		
		display_orders_detail: function(visibility,order,clickpos){
			var self = this;
			var contents = this.$('.client-details-contents');
			var parent   = this.$('.orders-line ').parent();
			var scroll   = parent.scrollTop();
			var height   = contents.height();
			contents.off('click','.button.edit');
			contents.off('click','.button.save');
			contents.off('click','.button.undo');
			
			contents.on('click','.button.save',function(){ self.save_client_details(order); });
			contents.on('click','.button.undo',function(){ self.undo_client_details(order); });


			this.editing_client = false;
			this.uploaded_picture = null;
			if(visibility === 'show'){
				contents.empty();
				
				
				//Custom Code for passing the orderlines
				var orderline = [];
				for (var z = 0; z < order.lines.length; z++){
					orderline.push(self.pos.db.get_lines_by_id[order.lines[z]])
				}
				//Custom code ends
				
				contents.append($(QWeb.render('OrderDetails',{widget:this,order:order,orderline:orderline,current_date:current_date})));

				var new_height   = contents.height();

				if(!this.details_visible){
					if(clickpos < scroll + new_height + 20 ){
						parent.scrollTop( clickpos - 20 );
					}else{
						parent.scrollTop(parent.scrollTop() + new_height);
					}
				}else{
					parent.scrollTop(parent.scrollTop() - height + new_height);
				}

				this.details_visible = true;
				//this.toggle_save_button();
			 } 
			 
			 else if (visibility === 'edit') {
			// Connect the keyboard to the edited field
			if (this.pos.config.iface_vkeyboard && this.chrome.widget.keyboard) {
				contents.off('click', '.detail');
				searchbox.off('click');
				contents.on('click', '.detail', function(ev){
					self.chrome.widget.keyboard.connect(ev.target);
					self.chrome.widget.keyboard.show();
				});
				searchbox.on('click', function() {
					self.chrome.widget.keyboard.connect($(this));
				});
			}

			this.editing_client = true;
			contents.empty();
			contents.append($(QWeb.render('ClientDetailsEdit',{widget:this})));

			contents.find('input').blur(function() {
				setTimeout(function() {
					self.$('.window').scrollTop(0);
				}, 0);
			});

			contents.find('.image-uploader').on('change',function(event){
				self.load_image_file(event.target.files[0],function(res){
					if (res) {
						contents.find('.client-picture img, .client-picture .fa').remove();
						contents.find('.client-picture').append("<img src='"+res+"'>");
						contents.find('.detail.picture').remove();
						self.uploaded_picture = res;
					}
				});
			});
			} 
			 
			 
			 
			 else if (visibility === 'hide') {
				contents.empty();
				if( height > scroll ){
					contents.css({height:height+'px'});
					contents.animate({height:0},400,function(){
						contents.css({height:''});
					});
				}else{
					parent.scrollTop( parent.scrollTop() - height);
				}
				this.details_visible = false;
				//this.toggle_save_button();
			}
		},
		
		get_selected_partner: function() {
			var self = this;
			if (self.gui)
				return self.gui.get_current_screen_param('selected_partner_id');
			else
				return undefined;
		},
		
		render_list_orders: function(orders, search_input){
			var self = this;
			var selected_partner_id = this.get_selected_partner();
			var selected_client_orders = [];
			if (selected_partner_id != undefined) {
				for (var i = 0; i < orders.length; i++) {
					if (orders[i].partner_id[0] == selected_partner_id)
						selected_client_orders = selected_client_orders.concat(orders[i]);
				}
				orders = selected_client_orders;
			}
			
		   if (search_input != undefined && search_input != '') {
				var selected_search_orders = [];
				var search_text = search_input.toLowerCase()
				for (var i = 0; i < orders.length; i++) {
					if (orders[i].partner_id == '') {
						orders[i].partner_id = [0, '-'];
					}
					if(orders[i].partner_id[1] == false)
					{
						if (((orders[i].name.toLowerCase()).indexOf(search_text) != -1) || ((orders[i].pos_reference.toLowerCase()).indexOf(search_text) != -1)) {
						selected_search_orders = selected_search_orders.concat(orders[i]);
						}
					}
					else
					{
						if (((orders[i].name.toLowerCase()).indexOf(search_text) != -1) || ((orders[i].pos_reference.toLowerCase()).indexOf(search_text) != -1) || ((orders[i].partner_id[1].toLowerCase()).indexOf(search_text) != -1)) {
						selected_search_orders = selected_search_orders.concat(orders[i]);
						}
					}
				}
				orders = selected_search_orders;
			}
			
			
			var content = this.$el[0].querySelector('.orders-list-contents');
			content.innerHTML = "";
			var orders = orders;
			var current_date = null;
			for(var i = 0, len = Math.min(orders.length,1000); i < len; i++){
				var order    = orders[i];
				current_date =  field_utils.format.datetime(moment(order.date_order), {type: 'datetime'});
				var ordersline_html = QWeb.render('OrdersLine',{widget: this, order:orders[i], selected_partner_id: orders[i].partner_id[0],current_date:current_date});
				var ordersline = document.createElement('tbody');
				ordersline.innerHTML = ordersline_html;
				ordersline = ordersline.childNodes[1];
				content.appendChild(ordersline);

			}
		},
		
		save_client_details: function(partner) {
			var self = this;
			
			var fields = {};
			this.$('.client-details-contents .detail').each(function(idx,el){
				fields[el.name] = el.value || false;
			});

			if (!fields.name) {
				this.gui.show_popup('error',_t('A Customer Name Is Required'));
				return;
			}
			
			if (this.uploaded_picture) {
				fields.image = this.uploaded_picture;
			}

			fields.id           = partner.id || false;
			fields.country_id   = fields.country_id || false;

			//new Model('res.partner').call('create_from_ui',[fields])
			rpc.query({
				model: 'res.partner',
				method: 'create_from_ui',
				args: [fields],
				
				}).then(function(partner_id){
				self.saved_client_details(partner_id);
			},function(err,event){
				event.preventDefault();
				self.gui.show_popup('error',{
					'title': _t('Error: Could not Save Changes'),
					'body': _t('Your Internet connection is probably down.'),
				});
			});
		},
		
		undo_client_details: function(partner) {
			this.display_orders_detail('hide');
			
		},
		
		saved_client_details: function(partner_id){
			var self = this;
			self.display_orders_detail('hide');
			alert('!! Customer Created Successfully !!')
			
		},
		
		
		
		
		show: function(options) {
			var self = this;
			this._super(options);
			
			this.details_visible = false;
			
			var orders = self.pos.db.all_orders_list;
			var orders_lines = self.pos.db.all_orders_line_list;
			this.render_list_orders(orders, undefined);
			
			this.$('.back').click(function(){
				self.gui.show_screen('products');
			});
			var current_date = null;
			//################################################################################################################
			this.$('.orders-list-contents').delegate('.orders-line-name', 'click', function(event) {
			   
			   for(var ord = 0; ord < orders.length; ord++){
				   if (orders[ord]['id'] == $(this).data('id')){
					var orders1 = orders[ord];
				   }
			   }
			   //var orders1 = self.pos.db.get_orders_by_id[parseInt($(this).data('id'))];
				current_date =  field_utils.format.datetime(moment(orders1.date_order),{type: 'datetime'});
			   var orderline = [];
			   for(var n=0; n < orders_lines.length; n++){
				   if (orders_lines[n]['order_id'][0] == $(this).data('id')){
					orderline.push(orders_lines[n])
				   }
			   }
				
				self.gui.show_popup('see_order_details_popup_widget', {'order': [orders1], 'orderline':orderline,'current_date':current_date});
			   
			});
			
			
			//################################################################################################################
			this.$('.orders-list-contents').delegate('.orders-line-ref', 'click', function(event) {
			   
			   
			   for(var ord = 0; ord < orders.length; ord++){
				   if (orders[ord]['id'] == $(this).data('id')){
					var orders1 = orders[ord];
				   }
			   }
			   //var orders1 = self.pos.db.get_orders_by_id[parseInt($(this).data('id'))];
				current_date =  field_utils.format.datetime(moment(orders1.date_order),{type: 'datetime'});
  
				var orderline = [];
				for(var n=0; n < orders_lines.length; n++){
					if (orders_lines[n]['order_id'][0] == $(this).data('id')){
					 orderline.push(orders_lines[n])
					}
				}
				
				self.gui.show_popup('see_order_details_popup_widget', {'order': [orders1], 'orderline':orderline,'current_date':current_date});
			   
			   
			});
						
			//################################################################################################################
			this.$('.orders-list-contents').delegate('.orders-line-partner', 'click', function(event) {
			   
			   
			   for(var ord = 0; ord < orders.length; ord++){
				   if (orders[ord]['id'] == $(this).data('id')){
					var orders1 = orders[ord];
				   }
			   }
			   
			   //var orders1 = self.pos.db.get_orders_by_id[parseInt($(this).data('id'))];
				current_date =  field_utils.format.datetime(moment(orders1.date_order),{type: 'datetime'});
				var orderline = [];
				for(var n=0; n < orders_lines.length; n++){
					if (orders_lines[n]['order_id'][0] == $(this).data('id')){
					 orderline.push(orders_lines[n])
					}
				}
				
				self.gui.show_popup('see_order_details_popup_widget', {'order': [orders1], 'orderline':orderline,'current_date':current_date});
			   
			});
			
			
			//################################################################################################################
			this.$('.orders-list-contents').delegate('.orders-line-date', 'click', function(event) {
			   
			   for(var ord = 0; ord < orders.length; ord++){
				   if (orders[ord]['id'] == $(this).data('id')){
					var orders1 = orders[ord];
				   }
			   }
			   
			   //var orders1 = self.pos.db.get_orders_by_id[parseInt($(this).data('id'))];
				current_date =  field_utils.format.datetime(moment(orders1.date_order),{type: 'datetime'});
				var orderline = [];
				for(var n=0; n < orders_lines.length; n++){
					if (orders_lines[n]['order_id'][0] == $(this).data('id')){
					 orderline.push(orders_lines[n])
					}
				}
				
				self.gui.show_popup('see_order_details_popup_widget', {'order': [orders1], 'orderline':orderline,'current_date':current_date});

			});
			
			//################################################################################################################
			
			this.$('.orders-list-contents').delegate('.orders-line-tot', 'click', function(event) {
		
				for(var ord = 0; ord < orders.length; ord++){
					if (orders[ord]['id'] == $(this).data('id')){
						var orders1 = orders[ord];
					}
				}
			
				//var orders1 = self.pos.db.get_orders_by_id[parseInt($(this).data('id'))];
				current_date =  field_utils.format.datetime(moment(orders1.date_order),{type: 'datetime'});
				var orderline = [];
				for(var n=0; n < orders_lines.length; n++){
					if (orders_lines[n]['order_id'][0] == $(this).data('id')){
					 orderline.push(orders_lines[n])
					}
				}
				self.gui.show_popup('see_order_details_popup_widget', {'order': [orders1], 'orderline':orderline,'current_date':current_date});
			});


			this.$('.orders-list-contents').delegate('.orders-line-state', 'click', function(event) {
		
				for(var ord = 0; ord < orders.length; ord++){
					if (orders[ord]['id'] == $(this).data('id')){
						var orders1 = orders[ord];
					}
				}
			
				//var orders1 = self.pos.db.get_orders_by_id[parseInt($(this).data('id'))];
				current_date =  field_utils.format.datetime(moment(orders1.date_order),{type: 'datetime'});
				var orderline = [];
				for(var n=0; n < orders_lines.length; n++){
					if (orders_lines[n]['order_id'][0] == $(this).data('id')){
					 orderline.push(orders_lines[n])
					}
				}
				self.gui.show_popup('see_order_details_popup_widget', {'order': [orders1], 'orderline':orderline,'current_date':current_date});
			});
			
			//this code is for Search Orders
			this.$('.search-order input').keyup(function() {
				self.render_list_orders(orders, this.value);
			});
			
			this.$('.new-customer').click(function(){
				self.display_orders_detail('edit',{
					'country_id': self.pos.company.country_id,
				});
			});

		},
		//
			   

	});
	gui.define_screen({
		name: 'see_all_orders_screen_widget',
		widget: SeeAllOrdersScreenWidget
	});

	// End SeeAllOrdersScreenWidget

	var SeeOrderDetailsPopupWidget = popups.extend({
		template: 'SeeOrderDetailsPopupWidget',
		
		init: function(parent, args) {
			this._super(parent, args);
			this.options = {};
		},
		
		
		show: function(options) {
			var self = this;
			options = options || {};
			this._super(options);
			
			
			this.order = options.order || [];
			this.orderline = options.orderline || [];
			this.current_date = options.current_date || [];
		},
		
		events: {
			'click .button.cancel': 'click_cancel',
		},
		
		renderElement: function() {
			var self = this;
			this._super();
		},

	});


	gui.define_popup({
		name: 'see_order_details_popup_widget',
		widget: SeeOrderDetailsPopupWidget
	});
	
	// Start SeeAllOrdersButtonWidget
	
	var SeeAllOrdersButtonWidget = screens.ActionButtonWidget.extend({
		template: 'SeeAllOrdersButtonWidget',

		button_click: function() {
			var self = this;
			this.gui.show_screen('see_all_orders_screen_widget', {});
		},
		
	});

	screens.define_action_button({
		'name': 'See All Orders Button Widget',
		'widget': SeeAllOrdersButtonWidget,
		'condition': function() {
			return true;
		},
	});
	// End SeeAllOrdersButtonWidget 

// Start ClientListScreenWidget
	gui.Gui.prototype.screen_classes.filter(function(el) { return el.name == 'clientlist'})[0].widget.include({
			show: function(){
				this._super();
				var self = this;
				this.$('.view-orders').click(function(){
					self.gui.show_screen('see_all_orders_screen_widget', {});
				});
			
			
			$('.selected-client-orders').on("click", function() {
				self.gui.show_screen('see_all_orders_screen_widget', {
					'selected_partner_id': this.id
				});
			});
			
		},
	});

	screens.ReceiptScreenWidget.include({
		handle_auto_print: function() {
			if (this.should_auto_print()) {
				setTimeout(function(){
					this.print();
				}, 500);
				if (this.should_close_immediately()){
					this.click_next();
				}
			} else {
				this.lock_screen(false);
			}
		},
	});
	
	return SeeAllOrdersScreenWidget;
});

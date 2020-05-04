odoo.define('pos_cash_inout_ext.inout', function(require) {
	"use strict";

	var gui = require('point_of_sale.gui');
	var models = require('point_of_sale.models');
	var screens = require('point_of_sale.screens');
	var core = require('web.core');
	var PopupWidget = require('point_of_sale.popups');
	var rpc = require('web.rpc');
	var QWeb = core.qweb;
	var _t = core._t;

	var PutMoneyIn = screens.ActionButtonWidget.extend({
		template : 'PutMoneyIn',
		button_click : function() {
		    this.gui.show_popup('cash_operation_popup', {
		    	button: this,
		    	title: "Put Money In",
		    	msg: 'Fill in this form if you put money in the cash register: ',
		    	operation: "put_money",
		    });
		}
	});
	screens.define_action_button({
		'name' : 'putmoneyin',
		'widget' : PutMoneyIn,
		'condition': function(){ return this.pos.config.enable_cash_in_out && this.pos.config.cash_control; },
	});
	var TakeMoneyOut = screens.ActionButtonWidget.extend({
		template : 'TakeMoneyOut',
		button_click : function() {
		    this.gui.show_popup('cash_operation_popup', {
		    	button: this,
		    	title: "Take Money Out",
		    	msg: 'Describe why you take money from the cash register: ',
		    	operation: "take_money",
		    });
		}
	});
	screens.define_action_button({
		'name' : 'TakeMoneyOut',
		'widget' : TakeMoneyOut,
		'condition': function(){ return this.pos.config.enable_cash_in_out && this.pos.config.cash_control; },
	});

	var CashInOutStatement = screens.ActionButtonWidget.extend({
	    template: 'CashInOutStatement',
	    button_click: function(){
            this.gui.show_popup('cash_inout_statement_popup');
	    }
	})
	screens.define_action_button({
		'name' : 'CashInOutStatement',
		'widget' : CashInOutStatement,
		'condition': function(){ return this.pos.config.enable_cash_in_out && this.pos.config.cash_control; },
	});

    var PrintCashInOutStatmentPopup = PopupWidget.extend({
        template: 'PrintCashInOutStatmentPopup',
        show: function(){
            var self = this;
            var users = self.pos.users;
            this._super();
			this.renderElement();
			var order = self.pos.get_order();
			this.$('.button.ok').click(function() {
			    var start_date = $('.start-date input').val() + ' 00:00:00';
			    var end_date = $('.end-date input').val() + ' 23:59:59';
			    var user_id = $('#user-id').find(":selected").text();
			    var domain = [];
			    order.set_statement_cashier(user_id);
                if(user_id){
                    if($('.start-date input').val() && $('.end-date input').val()){
                        domain = [['create_date', '>=', start_date],['create_date', '<=', end_date],['user_id', '=', Number($('#user-id').val())]];
                    }
                    else if($('.start-date input').val()){
                        domain = [['create_date', '>=', start_date],['user_id', '=', Number($('#user-id').val())]];
                    }
                    else if($('.end-date input').val()){
                        domain = [['create_date', '<=', end_date],['user_id', '=', Number($('#user-id').val())]];
                    }else{
                        domain = [['user_id', '=', Number($('#user-id').val())]];
                    }
                }else{
                    if($('.start-date input').val() && $('.end-date input').val()){
                        domain = [['create_date', '>=', start_date],['create_date', '<=', end_date]];
                    }
                    else if($('.start-date input').val()){
                        domain = [['create_date', '>=', start_date]];
                    }
                    else if($('.end-date input').val()){
                        domain = [['create_date', '<=', end_date]];
                    }else{
                        domain = [];
                    }
                }
                var params = {
                    model: 'cash.in.out.history',
                    method: 'search_read',
                    domain: domain,
                }
                rpc.query(params, {async: false}
                ).then(function(result){
                    var order = self.pos.get_order();
                    if(user_id && result){
                        order.set_cash_register(result);
                        if(start_date && end_date){
                            if(result.length > 0){
                                self.gui.show_screen('receipt');
                            }
                        }
                    }else{
                        var data = {};
                        users.map(function(user){
                            var new_records = [];
                            result.map(function(record){
                                if(record.user_id[0] == user.id){
                                    new_records.push(record)
                                }
                            });
                            data[user.id] = new_records;
                        });
                        var flag = false;
                        for (var key in data) {
                            if(data[key].length > 0){
                                flag = true;
                            }
                        }
                        if(flag){
                            order.set_cash_register(data);
                            self.gui.show_screen('receipt');
                        }
                    }
                });
			});
			this.$('.button.cancel').click(function() {
				self.gui.close_popup();
			});
        },
    });
    gui.define_popup({name:'cash_inout_statement_popup', widget: PrintCashInOutStatmentPopup});

    var CashOperationPopup = PopupWidget.extend({
        template: 'CashOperationPopup',
        show: function(options){
            this._super(options);
            $('.reason').focus();
        },
        click_confirm: function(){
            var self = this;
            var name = $('.reason').val() || false;
            var amount = $('.amount').val() || false;
            if(name =='' || amount == ''){
                alert("Please fill all fields.");
                $('.reason').focus();
            }else if(!$.isNumeric(amount)){
                alert("Please input valid amount");
                $('.amount').val('').focus();
            }else{
                var session_id = '';
                var vals = {
                    'session_id': self.pos.pos_session.id,
                    'name': name,
                    'amount': amount,
                    'operation': self.options.operation,
                    'cashier': self.pos.get_cashier().id,

                }
                var params = {
                    model: 'pos.session',
                    method: 'cash_in_out_operation',
                    args: [vals],
                }
                rpc.query(params, {async: false})
    //		    		new Model('pos.session').call('cash_in_out_operation', [vals])
                .then(function(result) {
                    if (result['error']) {
                        self.gui.show_popup('error',{
                            'title': _t('Cash Control Configuration'),
                            'body': _t('Please enable cash control for this session.'),
                        });
                    }else {
                        var order = self.pos.get_order();
                        var operation = self.options.operation == "take_money" ? 'Take Money Out' : 'Put Money In'
                        if(order && self.pos.config.print_receipt){
                            order.set_money_inout_details({
                                'operation': operation,
                                'reason': name,
                                'amount': amount,
                            });
                        }


                        self.gui.close_popup();
                        if(!self.pos.config.enable_cash_in_out){
                            var title = '',
                                body = 'Successfully ';
                            if(self.options.operation === "put_money"){
                                title = "Put Money In"
                            } else if(self.options.operation === "take_money"){
                                title = "Take Money Out"
                            }
                            body += title
                            self.gui.show_popup('alert',{
                                'title': _t(title),
                                'body': _t(body),
                            });
                        }
                        if (self.pos.config.iface_cashdrawer){
                            self.pos.proxy.open_cashbox();
                        }
                    }
                }).fail(function(error, event) {
                    if (error.code === -32098) {
                        alert("Server closed...");
                        event.preventDefault();
                    }
                });

            }
            if(self.pos.config.print_receipt){
                this.gui.show_screen('receipt');
            }
        },
    });
    gui.define_popup({name:'cash_operation_popup', widget: CashOperationPopup});

    screens.ReceiptScreenWidget.include({
        render_receipt: function(){
            var self = this;
            var order = self.pos.get('selectedOrder');
            if(order.get_money_inout_details()){
                if(order.get_money_inout_details()){
                    $('.pos-receipt-container', this.$el).html(QWeb.render('MoneyInOutTicket',{
                       widget:self,
                       order: order,
                       money_data: order.get_money_inout_details(),
                    }));
                }
            }else if(order.get_cash_register()){
                $('.pos-receipt-container', this.$el).html(QWeb.render('CashInOutStatementReceipt',{
                    widget:self,
                    order: order,
                    statements: order.get_cash_register(),
                }));
            }else{
                self._super();
            }
        },
    });

    models.Order = models.Order.extend({
        set_money_inout_details: function(money_inout_details){
            this.money_inout_details = money_inout_details;
        },
        get_money_inout_details: function(){
            return this.money_inout_details;
        },
        set_cash_register: function(result){
            this.result = result;
        },
        get_cash_register: function(){
            return this.result;
        },
        set_statement_cashier: function(user_id){
            this.user_id = user_id;
        },
        get_statement_cashier: function(){
            return this.user_id;
        }
    });
});

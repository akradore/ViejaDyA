
odoo.define('pos_credit_payment.pos', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var gui = require('point_of_sale.gui');
    var popups = require('point_of_sale.popups');
    //var Model = require('web.DataModel');
    

    var _t = core._t;

    var _super_posmodel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        initialize: function (session, attributes) {
            var partner_model = _.find(this.models, function(model){ return model.model === 'res.partner'; });
            partner_model.fields.push('custom_credit');
            
            var journal_model = _.find(this.models, function(model){ return model.model === 'account.journal'; });
            journal_model.fields.push('credit');
            return _super_posmodel.initialize.call(this, session, attributes);
        },
        // push_order: function(order, opts){
        //     var self = this;
        //     var pushed = _super_posmodel.push_order.call(this, order, opts);
        //     var client = order && order.get_client();
        //     var pos_cur =  self.config.currency_id[0];
        //     var company_id = self.config.company_id;  
        //     if (client){
        //         order.paymentlines.each(function(line){
        //             var journal = line.cashregister.journal;
        //             var amount = line.get_amount();
        //             if (journal['credit'] === true){
        //             // if (amount <= client.custom_credit){
        //             //   var updated = client.custom_credit - amount;
        //               //var model1 = new Model('res.partner');
        //             rpc.query({
        //                 model: 'res.partner',
        //                 method: 'UpdateCredit',
        //                 args: [1,client,company_id, pos_cur , amount],
        //                 // args: [[client.id], {'custom_credit': updated}],
        //             });
                    
        //               //model1.call('write', [client['id'], {'custom_credit' : updated}]).then(null);
        //             }
        //             else{
        //             }
        //            // }
        //         });
        //     }
        //     return pushed;
        // }
        //             var journal = line.cashregister.journal;
            
        //             var amount = line.get_amount();
        //             if (journal['credit'] === true){
        //             if (amount <= client.custom_credit){
        //               var updated = client.custom_credit - amount;
                      
        //               //var model1 = new Model('res.partner');
        //             rpc.query({
        //                 model: 'res.partner',
        //                 method: 'write',
        //                 args: [[client.id], {'custom_credit': updated}],
        //             });
                    
        //               //model1.call('write', [client['id'], {'custom_credit' : updated}]).then(null);
        //             }
        //             else{
        //             }
        //            }
        //         });
        //     }
        //     return pushed;
        // }
    });


  screens.PaymentScreenWidget.include({
        validate_order: function(options) {
            var self = this;
            var currentOrder = this.pos.get_order();
            
            var plines = currentOrder.get_paymentlines();
            
            var dued = currentOrder.get_due();
            
            var changed = currentOrder.get_change();
            
            var clients = currentOrder.get_client();
            var a = [];
            var pos_cur =  this.pos.config.currency_id[0];
            var company_id = this.pos.config.company_id;
            for(var i = 0; i < plines.length; i++) {
                if(plines[i].cashregister.journal['credit'] === true){
                    
                    a.push(plines[i]);
                }
            }
            
           
            if(currentOrder.get_orderlines().length === 0){
                    self.gui.show_popup('error',{
                        'title': _t('Empty Order'),
                        'body': _t('There must be at least one product in your order before it can be validated.'),
                    });
                    return;
                 }

            if (clients){  //if customer is selected
                if (a['length'] != 0) { //we've given Miscellaneous Type
                    for (var i = 0; i < plines.length; i++) {
                        if(plines[i].cashregister.journal['credit'] === true){
                        	 if(currentOrder.get_change() > 0){ // Make Condition that amount is greater than selected customer's credit amount
                       self.gui.show_popup('error',{
                        'title': _t('Payment Amount Exceeded'),
                        'body': _t('You cannot Pay More than Total Amount'),
                    });
                    return;
                }
                
                // Make Condition: Popup Occurs When Customer is not selected on credit payment method, While any other payment method, this error popup will not be showing
            if (!currentOrder.get_client()){
                    self.gui.show_popup('error',{
                        'title': _t('Unknown customer'),
                        'body': _t('You cannot use Credit payment. Select customer first.'),
                    });
                    return;
                }

                            var amount = plines[i].get_amount();
                            rpc.query({
                                model: 'res.partner',
                                method: 'CheckCredit',
                                args: [1,clients,company_id, pos_cur , amount]
                                // args: [[client.id], {'custom_credit': updated}],
                            }).then(function(output) {
                               if(output > clients.custom_credit){ // Make Condition that amount is greater than selected customer's credit amount
                                   // self.gui.show_popup('error',{
                                   //      'title': _t('Not Sufficient Credit'),
                                   //      'body': _t('Customer has not Sufficient Credit To Pay'),
                                   //  });
                                   alert('Customer has not Sufficient Credit To Pay')
                                    // break;
                                    return;
                                }else
                                {
                                    rpc.query({
                                    model: 'res.partner',
                                    method: 'UpdateCredit',
                                    args: [1,clients,company_id, pos_cur , amount],
                                    // args: [[client.id], {'custom_credit': updated}],
                                    }).then(function(output) {
                                        if(output==false){
                                             self.gui.show_popup('error',{
                                                'title': _t('Not Sufficient Credit'),
                                                'body': _t('Customer has not Sufficient Credit To Pay'),
                                            });
                                            return;
                                        }
                                        else{

                                            self.finalize_validation();
                                        }
                                    });
                                        }
                                });
                            }
                        }
               }else{
                 self.finalize_validation();
               }

                
             }else if(a['length'] == 0){
                this.finalize_validation();
             }else{
                self.gui.show_popup('error',{
                                    'title': _t('Unknown customer/use credit payment'),
                                    'body': _t('You cannot use Credit payment. Select customer first.'),
                                });
                                return;
             }
             
                   
                 //}
                 // else{
                 //    self.finalize_validation();
                 // }

           // a = [];

            // this._super(options);
        },

     
    });




});

frappe.ui.form.on("Quotation", "refresh", function(frm) {
  if(frm.doc.docstatus == 0) {
    frm.add_custom_button(__('Fetch Standard Price'), function(){
      
          
    frappe.call({
        method:"alfarsi_erpnext.alfarsi_erpnext.customer.fetch_standard_price",
        args:{"items":frm.doc.items,
                "price_list":frm.doc.selling_price_list,
                "party": frm.doc.party_name,
                "quotation_to": frm.doc.quotation_to
                
        },
        freeze: 1,
        callback: function(r){
          for (let i = 0; i < frm.doc.items.length; i++) {
            frm.doc.items[i].standard_price = r.message[frm.doc.items[i].item_code] ? r.message[frm.doc.items[i].item_code] : 0
            frm.doc.items[i].rate = r.message[frm.doc.items[i].item_code + "-negotiated"] ? r.message[frm.doc.items[i].item_code + "-negotiated"] : 0
          }
          frm.refresh_fields();
          frm.dirty();
        }
    })
    //  frm.save();
      
  })
}
});
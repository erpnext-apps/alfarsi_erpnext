frappe.ui.form.on("Purchase Receipt", {
	process: function(frm){
		if(frm.doc.scan){
			frappe.call({
				method: "alfarsi_erpnext.api.fetch_item_table",
				args: {
							doc: frm.doc
				},
				callback: (r) => {
					if(r.message){
						frm.set_value("scan",r.message.failed_to_process)
						frm.set_value("items",[])
						for(const element of r.message.items){
							let row = frm.add_child("items", element);
							frm.script_manager.trigger('item_code', row.doctype, row.name)
							frm.refresh_field("items");
						}
					}
				}
			  })
		}
		else{
			frappe.msgprint("Please scan the items Scan field is empty")
		}
	}
})
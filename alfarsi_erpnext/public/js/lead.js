frappe.ui.form.on("Lead", "refresh", function(frm) {
  frm.add_custom_button(__("User"), function() {
    frappe.call({
      method: "alfarsi_erpnext.alfarsi_erpnext.customer.create_user_from_lead",
      args: {
        email: cur_frm.doc.email_id,
        lead_name: cur_frm.doc.lead_name,
        docname: cur_frm.doc.name
      },
      callback: (result) => {
        if (!result || result.exc || !result.message) {
          me.render_error_feedback();
        } else {
          frappe.msgprint('User created succesfully!')
        }
      }
    })
  });
});
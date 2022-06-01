import frappe
from frappe import _, msgprint

def create_user_on_lead_creation(doc, method=None):
    quote_doc = frappe.get_doc('Quotation', frappe.cache().get_value('quote'))
    quote_doc.party_name = doc.name
    quote_doc.is_lead_registered = 1
    quote_doc.save()
    # if not doc.get("make_user"):
    #     return

    # customer_email = doc.get("email_id")
    # if not customer_email:
    #     msgprint(
    #         _("Skipped User creation due to missing Email."),
    #         title="Note"
    #     )
    #     return

    # user_exists = frappe.db.exists("User", {"email": customer_email})
    # if user_exists:
    #     return

    # user = frappe.get_doc({
    #     "doctype": "User",
    #     'send_welcome_email': 1,
    #     'email': customer_email,
    #     'first_name': doc.get("lead_name"),
    #     'user_type': 'Website User'
    # })

    # try:
    #     # user.add_roles("Customer")
    #     user.save(ignore_permissions=True)
    # except frappe.exceptions.OutgoingEmailError:
    #     msgprint(
    #         _("Failed to send welcome email."),
    #         alert=True
    #     )

@frappe.whitelist()
def create_user_from_lead(email, lead_name, docname=None):
    user_exists = frappe.db.exists("User", {"email": email})
    if user_exists:
        user = frappe.get_doc('User', {"email": email})
        for quote in frappe.db.get_list('Quotation', {'party_name': docname, 'docstatus': 0}, ['name']):
            frappe.db.set_value('Quotation', quote.name, 'owner', user.name)
            frappe.db.set_value('Quotation', quote.name, 'modified_by', user.name)
        return

    user = frappe.get_doc({
        "doctype": "User",
        'send_welcome_email': 1,
        'email': email,
        'first_name': lead_name,
        'user_type': 'Website User'
    })

    try:
        user.add_roles("Customer")
        user.save(ignore_permissions=True)

        for quote in frappe.db.get_list('Quotation', {'party_name': docname, 'docstatus': 0}, ['name']):
            frappe.db.set_value('Quotation', quote.name, 'owner', user.name)
            frappe.db.set_value('Quotation', quote.name, 'modified_by', user.name)
    except frappe.exceptions.OutgoingEmailError:
        msgprint(
            _("Failed to send welcome email."),
            alert=True
        )

@frappe.whitelist()
def approve_quote(name):
    from frappe.model.workflow import apply_workflow
    doc = frappe.get_doc('Quotation', name)
    try:
        apply_workflow(doc, "Approve")
    except:
        frappe.throw("Unable to approve now. Please contact the Sales Manager")

@frappe.whitelist()
def approve_quotation_items(quotation_item):
    parent_doc_name = frappe.db.get_value('Quotation Item', quotation_item, 'parent')
    if frappe.db.get_value('Quotation', parent_doc_name, 'docstatus') == 0:
        frappe.db.set_value('Quotation Item', quotation_item, 'rate_accepted', 1)
    else:
        frappe.throw("Not allowed to accept at this point")

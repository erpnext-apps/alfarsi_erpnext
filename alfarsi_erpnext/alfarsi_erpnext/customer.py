import frappe
from frappe import _, msgprint
from alfarsi_erpnext.alfarsi_erpnext.cart import get_party, _get_cart_quotation
from frappe.contacts.doctype.address.address import get_address_display


def transfer_quote_to_lead(doc, method=None):
    party = get_party('unapprovedlead@alfarsi.me')
    quote_identifier = frappe.request.cookies.get('guest_cart')

    quotation = _get_cart_quotation(party, quote_identifier)
    quote_doc = frappe.get_doc('Quotation', quotation.name)
    quote_doc.quotation_to = "Lead"
    quote_doc.party_name = doc.name
    quote_doc.customer_name = doc.company_name
    quote_doc.is_lead_registered = 1

    address_names = frappe.db.get_all(
        "Dynamic Link",
        fields=("parent"),
        filters=dict(parenttype="Address", link_doctype="Lead", link_name=doc.name),
    )

    if address_names:
        address_name = address_names[0].name
        address_doc = frappe.get_doc("Address", address_names[0].name).as_dict()
        address_display = get_address_display(address_doc)

        quote_doc.customer_address = address_name
        quote_doc.address_display = address_display
        quote_doc.shipping_address_name = address_name
    
    contact_names = frappe.db.get_all(
        "Dynamic Link",
        fields=("parent"),
        filters=dict(parenttype="Contact", link_doctype="Lead", link_name=doc.name),
    )

    if contact_names:
        contact_name = contact_names[0].name
        quote_doc.contact_person = contact_name
        quote_doc.contact_display = None

    quote_doc.save()
    frappe.local.cookie_manager.set_cookie("cart_count", 0)
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
        for quote in frappe.db.get_list('Quotation', {'party_name': docname, 'docstatus': 0}, ['name', 'customer_name']):
            frappe.db.set_value('Quotation', quote.name, 'owner', user.name)
            frappe.db.set_value('Quotation', quote.name, 'modified_by', user.name)
            frappe.rename_doc('Quotation', quote.name, quote.customer_name)
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

        for quote in frappe.db.get_list('Quotation', {'party_name': docname, 'docstatus': 0}, ['name', 'customer_name']):
            frappe.db.set_value('Quotation', quote.name, 'owner', user.name)
            frappe.db.set_value('Quotation', quote.name, 'modified_by', user.name)
            frappe.db.set_value('Quotation', quote.name, 'title', quote.customer_name)
    except frappe.exceptions.OutgoingEmailError:
        msgprint(
            _("Failed to send welcome email."),
            alert=True
        )

@frappe.whitelist()
def approve_quote(name, approve_all = 0):
    from frappe.model.workflow import apply_workflow
    doc = frappe.get_doc('Quotation', name)
    try:
        if not approve_all:
            unapproved_items = []
            to_remove = []
            for item in doc.items:
                if not item.rate_accepted:
                    unapproved_items.append({
                        "item_code": item.item_code,
                        "rate": item.rate,
                        "qty": item.qty,
                        "uom": item.uom
                    })
                    to_remove.append(item)
            for unapproved_item in unapproved_items:
                doc.append('unapproved_items', unapproved_item)
            
            for d in to_remove:
                doc.remove(d)
        else:
            for item in doc.items:
                item.rate_accepted = 1
        doc.save()
        apply_workflow(doc, "Approve")
    except:
        frappe.db.rollback()
        frappe.throw("Unable to approve now. Please contact the Sales Manager")
        return False
    return True

@frappe.whitelist()
def approve_quotation_items(quotation_item):
    parent_doc_name = frappe.db.get_value('Quotation Item', quotation_item, 'parent')
    if frappe.db.get_value('Quotation', parent_doc_name, 'docstatus') == 0:
        if frappe.db.get_value('Quotation Item', quotation_item, 'rate_accepted'):
            frappe.db.set_value('Quotation Item', quotation_item, 'rate_accepted', 0)
        else:
            frappe.db.set_value('Quotation Item', quotation_item, 'rate_accepted', 1)
    else:
        frappe.throw("Not allowed to modify at this point")
    return frappe.db.get_value('Quotation Item', quotation_item, 'rate_accepted')




    
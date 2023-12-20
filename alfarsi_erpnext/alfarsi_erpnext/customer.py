import frappe
from frappe import _, msgprint
from alfarsi_erpnext.alfarsi_erpnext.cart import get_party, _get_cart_quotation
from frappe.contacts.doctype.address.address import get_address_display


def transfer_quote_to_lead(doc, method=None):
    party = get_party('unapprovedlead@alfarsi.me')
    quote_identifier = frappe.request.cookies.get('guest_cart')

    quotation = _get_cart_quotation(party, quote_identifier)
    if not quotation.name:
        return
    
    contact = frappe.new_doc("Contact")
    contact.first_name = doc.lead_name
    contact.add_email(doc.email_id, is_primary=True)
    contact.add_phone(doc.mobile_no, is_primary_phone=True)

    contact.append("links", {"link_doctype": "Lead", "link_name": doc.name})

    contact.flags.ignore_mandatory = True
    contact.save(ignore_permissions=True)

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

def transfer_quote_to_lead_on_login(login_manager, method=None):
    party = get_party('unapprovedlead@alfarsi.me')
    quote_identifier = frappe.request.cookies.get('guest_cart')
    if not quote_identifier:
        return
    
    open_quote = frappe.db.get_value("Quotation", {"session_uuid": quote_identifier, "is_lead_registered": 0}, "name")
    if not open_quote:
        return

    customer = frappe.get_all(
        "Customer", filters={"email_id": frappe.session.user}
    )
    customer = [customer.name for customer in customer]
    matching_customer = None
    if len(customer) > 0:
        matching_customer = frappe.get_doc("Customer", customer[0])
        quotation_to = "Customer"
  
    if not matching_customer:
        return

    quotation = _get_cart_quotation(party, quote_identifier)
    if not quotation:
        return
    quote_doc = frappe.get_doc('Quotation', quotation.name)
    quote_doc.quotation_to = quotation_to
    quote_doc.party_name = matching_customer.name
    quote_doc.customer_name = matching_customer.name
    quote_doc.is_lead_registered = 1

    address_names = frappe.db.get_all(
        "Dynamic Link",
        fields=("parent"),
        filters=dict(parenttype="Address", link_doctype="Customer", link_name=matching_customer.name),
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
        filters=dict(parenttype="Contact", link_doctype="Customer", link_name=matching_customer.name),
    )

    if contact_names:
        contact_name = contact_names[0].name
        quote_doc.contact_person = contact_name
        quote_doc.contact_display = None

    quote_doc.save()
    frappe.local.cookie_manager.set_cookie("cart_count", 0)

def validate_email(doc, method=None):
    duplicate_leads = frappe.get_all(
        "Lead", filters={"email_id": doc.email_id, "name": ["!=", doc.name]}
    )
    duplicate_leads = [lead.name for lead in duplicate_leads]
    if duplicate_leads:
        frappe.throw("An account with this email id already exists. Please login")


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

@frappe.whitelist()
def request_logged_user_quote(name):
    if not name:
        return False
    frappe.db.set_value("Quotation", name, "is_lead_registered", 1)
    return True

@frappe.whitelist()
def fetch_standard_price(items, price_list, party, quotation_to):
    import json
    items = json.loads(items)
    customer = None
    if quotation_to == 'Customer':
        customer = frappe.db.get_value("Customer", party)
    if quotation_to == 'Lead':
        customer = frappe.db.get_value("Customer", {"lead_name": party})
    result = {}
    for item in items:
        result[item['item_code']] = frappe.db.get_value("Item Price",{"price_list": price_list, "item_code": item['item_code'], "selling": 1}, "price_list_rate")
        result[item['item_code'] + "-negotiated"] = frappe.db.get_value("Item Price",{"price_list": price_list, "item_code": item['item_code'], "customer": customer, "selling": 1}, "price_list_rate")
    return result






    
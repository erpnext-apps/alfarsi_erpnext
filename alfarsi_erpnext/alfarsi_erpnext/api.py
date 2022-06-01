import json

import frappe
from frappe.utils import cint, cstr

from erpnext.e_commerce.shopping_cart.cart import _get_cart_quotation, _set_price_list
from erpnext.e_commerce.doctype.e_commerce_settings.e_commerce_settings import (
	get_shopping_cart_settings,
)
from erpnext.utilities.product import get_price as get_desk_price

from erpnext.controllers.website_list_for_contact import (
	is_website_user, 
	rfq_transaction_list, 
	post_process, 
	get_list_for_transactions,
	get_customer_field_name,
	has_common)

@frappe.whitelist(allow_guest=True)
def bulk_add_to_cart(item_list=None):
	settings = get_shopping_cart_settings()

	if not settings.get("enabled") or frappe.session.user == "Guest":
		return

	if isinstance(item_list, str):
		item_list = json.loads(item_list)

	# validate items
	for item in item_list:
		if not frappe.db.exists("Item", {"item_code": item}):
			return {"exc": f"SKU '{item}' does not exist"}

		entry = item_list.get(item)
		qty = cint(entry.get("qty"))
		id = cint(entry.get("id"))

		if qty <= 0:
			return {"exc": f"Row #{id}: Qty must be atleast 1"}

	# bulk add items
	quotation = _get_cart_quotation()

	for item in item_list:
		quotation_items = quotation.get("items", {"item_code": item})
		entry = item_list.get(item)
		qty = cint(entry.get("qty"))

		if not quotation_items:
			quotation.append("items", {
				"doctype": "Quotation Item",
				"item_code": item,
				"qty": qty
			})
		else:
			quotation_items[0].qty = qty

	quotation.flags.ignore_permissions = True
	quotation.payment_schedule = []
	quotation.save()

	# set cart count
	cart_count = cstr(len(quotation.get("items")))
	if hasattr(frappe.local, "cookie_manager"):
		frappe.local.cookie_manager.set_cookie("cart_count", cart_count)

	return quotation.get("name")

@frappe.whitelist(allow_guest=True)
def get_price(item_code=None):
	settings = get_shopping_cart_settings()

	price = "NA"
	if settings.show_price:
		selling_price_list = _set_price_list(settings, None)
		price = get_desk_price(
			item_code,
			selling_price_list,
			settings.default_customer_group,
			settings.company
		)

		if price:
			return price.get("formatted_price") or "NA"

	return price or "NA"

def update_website_context(context):
	context["get_list"] = get_transaction_list


def get_transaction_list(
	doctype,
	txt=None,
	filters=None,
	limit_start=0,
	limit_page_length=20,
	order_by="modified",
	custom=False,
):
	user = frappe.session.user
	ignore_permissions = False

	if not filters:
		filters = []

	if doctype in ["Supplier Quotation", "Purchase Invoice"]:
		filters.append((doctype, "docstatus", "<", 2))
	elif doctype in ["Quotation"]:
		filters.append((doctype, "docstatus", "=", 0))
		filters.append(("workflow_state", "=", "Ready for Customer Review"))
	else:
		filters.append((doctype, "docstatus", "=", 1))

	if (user != "Guest" and is_website_user()) or doctype == "Request for Quotation":
		parties_doctype = (
			"Request for Quotation Supplier" if doctype == "Request for Quotation" else doctype
		)
		# find party for this contact
		customers, suppliers, leads = get_customers_suppliers(parties_doctype, user)

		if customers:
			if doctype == "Quotation":
				filters.append(("quotation_to", "=", "Customer"))
				filters.append(("party_name", "in", customers))
			else:
				filters.append(("customer", "in", customers))
		elif suppliers:
			filters.append(("supplier", "in", suppliers))
		elif leads:
			filters.append(("party_name", "in", leads))
		elif not custom:
			return []

		if doctype == "Request for Quotation":
			parties = customers or suppliers
			return rfq_transaction_list(parties_doctype, doctype, parties, limit_start, limit_page_length)

		# Since customers and supplier do not have direct access to internal doctypes
		ignore_permissions = True

		if not customers and not suppliers and custom:
			ignore_permissions = False
			filters = []

	transactions = get_list_for_transactions(
		doctype,
		txt,
		filters,
		limit_start,
		limit_page_length,
		fields="name",
		ignore_permissions=ignore_permissions,
		order_by="modified desc",
	)

	if custom:
		return transactions

	return post_process(doctype, transactions)

def get_customers_suppliers(doctype, user):
	customers = []
	suppliers = []
	leads= []
	meta = frappe.get_meta(doctype)

	customer_field_name = get_customer_field_name(doctype)

	has_customer_field = meta.has_field(customer_field_name)
	has_supplier_field = meta.has_field("supplier")

	if has_common(["Supplier", "Customer"], frappe.get_roles(user)):
		contacts = frappe.db.sql(
			"""
			select
				`tabContact`.email_id,
				`tabDynamic Link`.link_doctype,
				`tabDynamic Link`.link_name
			from
				`tabContact`, `tabDynamic Link`
			where
				`tabContact`.name=`tabDynamic Link`.parent and `tabContact`.email_id =%s
			""",
			user,
			as_dict=1,
		)
		customers = [c.link_name for c in contacts if c.link_doctype == "Customer"]
		suppliers = [c.link_name for c in contacts if c.link_doctype == "Supplier"]
		leads = [c.link_name for c in contacts if c.link_doctype == "Lead"]
	elif frappe.has_permission(doctype, "read", user=user):
		customer_list = frappe.get_list("Customer")
		customers = suppliers = [customer.name for customer in customer_list]

	return customers if has_customer_field else None, suppliers if has_supplier_field else None, leads if has_customer_field else None


def has_website_permission(doc, ptype, user, verbose=False):
	doctype = doc.doctype
	customers, suppliers, leads = get_customers_suppliers(doctype, user)
	if customers:
		return frappe.db.exists(doctype, get_customer_filter(doc, customers))
	elif suppliers:
		fieldname = "suppliers" if doctype == "Request for Quotation" else "supplier"
		return frappe.db.exists(doctype, {"name": doc.name, fieldname: ["in", suppliers]})
	elif leads:
		# import pdb; pdb.set_trace()
		return frappe.db.exists(doctype, get_lead_filter(doc, leads))
	else:
		return False


def get_customer_filter(doc, customers):
	doctype = doc.doctype
	filters = frappe._dict()
	filters.name = doc.name
	filters[get_customer_field_name(doctype)] = ["in", customers]
	if doctype == "Quotation":
		filters.quotation_to = "Customer"
	return filters

def get_lead_filter(doc, leads):
	doctype = doc.doctype
	filters = frappe._dict()
	filters.name = doc.name
	filters[get_customer_field_name(doctype)] = ["in", leads]
	filters.quotation_to = "Lead"
	return filters
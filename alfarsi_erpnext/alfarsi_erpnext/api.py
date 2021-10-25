import json

import frappe
from frappe.utils import cint, cstr

from erpnext.e_commerce.shopping_cart.cart import _get_cart_quotation, _set_price_list
from erpnext.e_commerce.doctype.e_commerce_settings.e_commerce_settings import (
	get_shopping_cart_settings,
)
from erpnext.utilities.product import get_price as get_desk_price

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
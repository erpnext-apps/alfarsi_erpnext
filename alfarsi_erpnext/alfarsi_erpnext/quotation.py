import frappe
from erpnext.selling.doctype.quotation.quotation import Quotation
from alfarsi_erpnext.alfarsi_erpnext.api import alfarsi_has_website_permission

class CustomQuotation(Quotation):
	def has_website_permission(doc, ptype, user, verbose=False):
		return alfarsi_has_website_permission(doc, ptype, user, verbose=False)
import frappe
from frappe import _, msgprint

def create_user_on_lead_creation(doc, method=None):
    if not doc.get("make_user"):
        return

    customer_email = doc.get("email_id")
    if not customer_email:
        msgprint(
            _("Skipped User creation due to missing Email."),
            title="Note"
        )
        return

    user_exists = frappe.db.exists("User", {"email": customer_email})
    if user_exists:
        return

    user = frappe.get_doc({
        "doctype": "User",
        'send_welcome_email': 1,
        'email': customer_email,
        'first_name': doc.get("lead_name"),
        'user_type': 'Website User'
    })

    try:
        user.add_roles("Customer")
        user.save(ignore_permissions=True)
    except frappe.exceptions.OutgoingEmailError:
        msgprint(
            _("Failed to send welcome email."),
            alert=True
        )
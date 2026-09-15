import frappe


def execute():
	"""Localization seam: every existing property is India (that's all we had
	before packs). clear_cache so the new kamra_localization hook is seen."""
	if frappe.db.has_column("Property", "country"):
		frappe.db.sql("UPDATE `tabProperty` SET country='India' WHERE COALESCE(country,'')=''")
		frappe.db.sql("UPDATE `tabProperty` SET currency='INR' WHERE COALESCE(currency,'')=''")
		frappe.db.sql("UPDATE `tabProperty` SET locale='en-IN' WHERE COALESCE(locale,'')=''")
	frappe.clear_cache()

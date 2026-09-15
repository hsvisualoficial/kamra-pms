"""Accounting export: hand closed invoices to the books. Kamra keeps the front
office; your ledger (Tally, Zoho, ERPNext, ...) keeps compliance. The tax
columns are shaped by the property's localization pack, so an India export
carries CGST/SGST and a VAT country carries a single Tax column - the core
never hardcodes it. This is the folio -> GL boundary, made downloadable and
entirely optional (IRN / live e-invoicing stays a per-country pack concern)."""

import frappe

from kamra.authz import require_roles


@frappe.whitelist()
@require_roles("Finance", "Hotel Admin", "Kamra Agent")
def export_invoices(property: str, from_date: str, to_date: str):
	"""Every closed invoice in the window as accounting rows: one voucher per
	invoice, taxable value, tax split (pack-shaped), party and identifiers."""
	from kamra.api import folio_invoice
	from kamra.localization import pack_for

	prop = frappe.get_cached_doc("Property", property)
	ctx = pack_for(property).invoice_context(prop)
	components = [c for c, _ in ctx["split"]]  # ['cgst','sgst'] or ['tax']
	ratios = {c: float(r) for c, r in ctx["split"]}

	names = frappe.get_all(
		"Folio",
		filters={"property": property, "status": "Closed",
		         "invoice_number": ["is", "set"],
		         "closed_on": ["between",
		                       [from_date + " 00:00:00", to_date + " 23:59:59"]]},
		pluck="name", order_by="closed_on asc")

	rows = []
	for fn in names:
		inv = folio_invoice(fn)
		f = inv["folio"]
		bt = inv.get("bill_to")
		taxable = round(sum(float(s["taxable"]) for s in inv["gst_summary"]), 2)
		total_tax = round(sum(float(s["total_tax"]) for s in inv["gst_summary"]), 2)
		row = {
			"invoice_number": f.get("invoice_number"),
			"date": str(f.get("closed_on"))[:10],
			"party": (bt["name"] if bt else f.get("guest_name")) or "Guest",
			"party_tax_id": (bt.get("gstin") if bt else "") or "",
			"place_of_supply": inv["property"].get("place_of_supply") or "",
			"service_code": inv["property"].get("sac") or "",
			"taxable": taxable,
			"total_tax": total_tax,
			"grand_total": round(float(f.get("grand_total") or 0), 2),
		}
		for c in components:
			row[c] = round(total_tax * ratios[c], 2)
		rows.append(row)

	totals = {
		"invoices": len(rows),
		"taxable": round(sum(r["taxable"] for r in rows), 2),
		"total_tax": round(sum(r["total_tax"] for r in rows), 2),
		"grand_total": round(sum(r["grand_total"] for r in rows), 2),
	}
	return {
		"rows": rows,
		"components": components,           # tax column keys, in order
		"tax_label": ctx["tax_label"],      # "GST" / "Tax"
		"tax_id_label": ctx["tax_id_label"],  # "GSTIN" / "Tax ID"
		"currency": prop.get("currency") or "INR",
		"totals": totals,
	}

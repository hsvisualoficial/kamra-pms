# Copyright (c) 2026, HeyKoala and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate


class RoomBlock(Document):
	def validate(self):
		if getdate(self.to_date) <= getdate(self.from_date):
			frappe.throw(_("The block's 'To' date must be after its 'From' date."))
		self.validate_room_property()
		if self.block_status == "Active":
			self.validate_no_reservation_clash()

	def validate_room_property(self):
		room_prop = frappe.db.get_value("Room", self.room, "property")
		if room_prop and room_prop != self.property:
			frappe.throw(_("Room {0} is not in {1}.").format(
				self.room, self.property))

	def validate_no_reservation_clash(self):
		"""Can't hold a room that's already sold for an overlapping night -
		move the guest first."""
		clash = frappe.db.sql(
			"""
			SELECT name, guest_name, check_in_date FROM `tabReservation`
			WHERE room = %(room)s
			  AND status IN ('Confirmed', 'Checked In')
			  AND check_in_date < %(to)s
			  AND GREATEST(check_out_date,
			               DATE_ADD(check_in_date, INTERVAL 1 DAY)) > %(from)s
			LIMIT 1
			""",
			{"room": self.room, "from": self.from_date, "to": self.to_date},
			as_dict=True,
		)
		if clash:
			c = clash[0]
			frappe.throw(_(
				"Room is booked ({0}, {1}, arriving {2}) during this window. "
				"Move or cancel that stay before holding the room."
			).format(c.name, c.guest_name or "guest", c.check_in_date))

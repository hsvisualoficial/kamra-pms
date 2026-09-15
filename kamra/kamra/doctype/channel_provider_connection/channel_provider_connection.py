import frappe
from frappe.model.document import Document


class ChannelProviderConnection(Document):
	def validate(self):
		# Enforce one active connection per (property, channel). Two live voice
		# lines on the same property would confuse inbound routing.
		if self.active:
			existing = frappe.get_all(
				"Channel Provider Connection",
				filters={
					"property": self.property,
					"channel": self.channel,
					"active": 1,
					"name": ["!=", self.name],
				},
				pluck="name",
				limit=1,
			)
			if existing:
				frappe.throw(
					f"Another active {self.channel} connection already exists "
					f"for {self.property}: {existing[0]}. Deactivate it first."
				)

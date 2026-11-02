# Copyright (c) 2026, Asante Solutions and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class OnePin(Document):
	def autoname(self):
		self.name = f"{self.user}:{self.pin_key}"

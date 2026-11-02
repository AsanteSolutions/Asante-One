# Copyright (c) 2026, Asante Solutions and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class OneDepartmentProfile(Document):
	def validate(self):
		for reminder in self.reminders:
			if reminder.rule in ("Monthly on day", "Yearly on date") and not 1 <= (reminder.day or 0) <= 31:
				frappe.throw(_("Row {0}: day must be between 1 and 31").format(reminder.idx))

# Copyright (c) 2026, Asante Solutions and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate


class OneAnnouncement(Document):
	def validate(self):
		if self.show_until and getdate(self.show_until) < getdate(self.publish_from):
			frappe.throw(_("Show until must be on or after the publish date"))

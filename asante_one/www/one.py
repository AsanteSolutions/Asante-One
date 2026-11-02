from urllib.parse import quote

import frappe

from asante_one.api.boot import get_boot

no_cache = 1


def get_context(context):
	if frappe.session.user == "Guest":
		frappe.local.flags.redirect_location = "/login?redirect-to=" + quote(frappe.request.path)
		raise frappe.Redirect

	csrf_token = frappe.sessions.get_csrf_token()
	frappe.db.commit()  # nosemgrep: the csrf token must be saved before the page renders
	context = frappe._dict()
	# Each key becomes a global in one.html (frappe-ui's jinja boot data)
	context.boot = {"csrf_token": csrf_token, "site_name": frappe.local.site, "one": get_boot()}
	return context

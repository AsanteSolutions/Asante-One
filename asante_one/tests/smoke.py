"""The employee user the Playwright smoke tests sign in as (frontend/tests/smoke.mjs), for CI.

bench --site test_site execute asante_one.tests.smoke.create_employee_user
"""

import frappe

USER = "one-smoke@example.com"
PASSWORD = "Smoke-test-only-1"


def create_employee_user():
	# A known password on a real site would be a way in, so this only runs where tests may
	if not frappe.conf.allow_tests:
		frappe.throw("Only for a test site: set allow_tests first")
	if not frappe.db.exists("User", USER):
		frappe.get_doc(
			{
				"doctype": "User",
				"email": USER,
				"first_name": "Smoke",
				"last_name": "Test",
				"send_welcome_email": 0,
				"roles": [{"role": "Employee"}],
			}
		).insert(ignore_permissions=True)
	user = frappe.get_doc("User", USER)
	user.new_password = PASSWORD
	user.save(ignore_permissions=True)
	frappe.db.commit()

from datetime import date

import frappe
from frappe.tests import IntegrationTestCase, UnitTestCase

from asante_one.api import cache
from asante_one.api.boot import build_content, can_see
from asante_one.api.home import anniversaries, get_announcements, in_audience, mark_announcements_seen
from asante_one.api.life import get_event, get_life


class UnitTestRules(UnitTestCase):
	def test_leap_day_birthday_falls_on_28_february(self):
		born = date(2000, 2, 29)
		self.assertEqual(list(anniversaries(born, date(2027, 1, 1), date(2027, 12, 31))), [date(2027, 2, 28)])
		self.assertEqual(list(anniversaries(born, date(2028, 1, 1), date(2028, 12, 31))), [date(2028, 2, 29)])

	def test_birthdays_across_new_year(self):
		self.assertEqual(
			list(anniversaries(date(1990, 3, 1), date(2026, 10, 30), date(2027, 3, 31))), [date(2027, 3, 1)]
		)
		self.assertEqual(
			list(anniversaries(date(1990, 10, 30), date(2026, 10, 30), date(2027, 1, 28))),
			[date(2026, 10, 30)],
		)

	def test_audience(self):
		employee = frappe._dict(department="Operations", branch="Durban Branch")
		self.assertTrue(in_audience(frappe._dict(audience="All"), None, []))
		self.assertTrue(
			in_audience(frappe._dict(audience="Department", department="Operations"), employee, [])
		)
		self.assertFalse(in_audience(frappe._dict(audience="Department", department="Sales"), employee, []))
		self.assertFalse(in_audience(frappe._dict(audience="Branch", branch="Durban Branch"), None, []))
		self.assertTrue(
			in_audience(frappe._dict(audience="Role", role="HR Manager"), employee, ["HR Manager"])
		)

	def test_empty_roles_mean_everyone_and_admins_see_all(self):
		self.assertTrue(can_see([], ["Employee"]))
		self.assertFalse(can_see(["HR Manager"], ["Employee"]))
		self.assertTrue(can_see(["HR Manager"], ["Employee", "Asante One Admin"]))


class IntegrationTestAPI(IntegrationTestCase):
	def test_restricted_resource_never_reaches_an_employee(self):
		frappe.get_doc(
			{
				"doctype": "One Resource",
				"title": "Test restricted folder",
				"url": "https://drive.google.com/test-restricted",
				"category": "People and HR",
				"restricted_roles": [{"role": "HR Manager"}],
			}
		).insert()
		cache.clear()

		def urls(roles):
			return {item.get("url") for item in build_content(roles)["search"]}

		self.assertNotIn("https://drive.google.com/test-restricted", urls(["Employee"]))
		self.assertIn("https://drive.google.com/test-restricted", urls(["Employee", "HR Manager"]))

	def test_announcement_pops_up_once(self):
		announcement = frappe.get_doc(
			{"doctype": "One Announcement", "title": "Test pop up", "published": 1, "audience": "All"}
		).insert()

		def mine():
			return next(
				a for a in get_announcements(None, frappe.get_roles()) if a["name"] == announcement.name
			)

		self.assertFalse(mine()["seen"])
		mark_announcements_seen([announcement.name])
		self.assertTrue(mine()["seen"])
		# Marking again does not create a second row
		mark_announcements_seen([announcement.name])
		self.assertEqual(frappe.db.count("One Announcement View", {"announcement": announcement.name}), 1)

	def test_unpublished_and_expired_announcements_stay_hidden(self):
		hidden = [
			frappe.get_doc({"doctype": "One Announcement", "title": "Draft", "published": 0}).insert().name,
			frappe.get_doc(
				{
					"doctype": "One Announcement",
					"title": "Expired",
					"published": 1,
					"publish_from": "2026-01-01 08:00:00",
					"show_until": "2026-01-31",
				}
			)
			.insert()
			.name,
		]
		shown = {a["name"] for a in get_announcements(None, frappe.get_roles())}
		self.assertFalse(shown.intersection(hidden))

	def test_private_event_is_not_found(self):
		private = frappe.get_doc(
			{
				"doctype": "Event",
				"subject": "Test private appointment",
				"starts_on": "2026-11-20 09:00:00",
				"event_type": "Private",
			}
		).insert()
		company = frappe.get_doc(
			{
				"doctype": "Event",
				"subject": "Test team braai",
				"starts_on": "2026-11-21 12:00:00",
				"event_type": "Public",
				"one_category": "Social",
			}
		).insert()

		self.assertEqual(get_event(company.name)["title"], "Test team braai")
		self.assertRaises(frappe.DoesNotExistError, get_event, private.name)
		titles = {item["title"] for item in get_life("2026-11-01", "2026-11-30")}
		self.assertIn("Test team braai", titles)
		self.assertNotIn("Test private appointment", titles)

	def test_life_refuses_a_very_long_range(self):
		self.assertRaises(frappe.ValidationError, get_life, "2026-01-01", "2028-01-01")

	def test_employee_cannot_open_admin_doctypes(self):
		user = "one-test-employee@example.com"
		if not frappe.db.exists("User", user):
			frappe.get_doc(
				{"doctype": "User", "email": user, "first_name": "Test", "roles": [{"role": "Employee"}]}
			).insert()
		admin_doctypes = frappe.get_all(
			"DocType", filters={"module": "Asante One", "istable": 0}, pluck="name"
		)
		self.assertTrue(admin_doctypes)
		for doctype in admin_doctypes:
			self.assertFalse(frappe.has_permission(doctype, "read", user=user), doctype)
			self.assertFalse(frappe.has_permission(doctype, "write", user=user), doctype)
		self.assertTrue(frappe.has_permission("One Settings", "write", user="Administrator"))

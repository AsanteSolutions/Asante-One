from datetime import date

import frappe
from frappe.tests import IntegrationTestCase, UnitTestCase

from asante_one.api import cache
from asante_one.api.boot import build_content, can_see
from asante_one.api.home import get_announcements, in_audience, mark_announcements_seen, next_occurrence


class UnitTestRules(UnitTestCase):
	def test_leap_day_birthday_falls_on_28_february(self):
		self.assertEqual(next_occurrence(date(2000, 2, 29), date(2027, 1, 10)), date(2027, 2, 28))
		self.assertEqual(next_occurrence(date(2000, 2, 29), date(2028, 1, 10)), date(2028, 2, 29))

	def test_birthday_already_past_moves_to_next_year(self):
		self.assertEqual(next_occurrence(date(1990, 3, 1), date(2026, 10, 30)), date(2027, 3, 1))
		self.assertEqual(next_occurrence(date(1990, 10, 30), date(2026, 10, 30)), date(2026, 10, 30))

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

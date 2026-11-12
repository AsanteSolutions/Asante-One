from datetime import date

import frappe
from frappe.tests import IntegrationTestCase, UnitTestCase

from asante_one.api.equipment import get_equipment, net_holdings, validate_stock_entry

OFFICE, SITE = "Office - AS", "Site - AS"


def move(employee, item, qty, day, out=True, purpose=None):
	source, target = (OFFICE, SITE) if out else (SITE, OFFICE)
	return frappe._dict(
		asset_champion=employee,
		item_code=item,
		s_warehouse=source,
		t_warehouse=target,
		transfer_qty=qty,
		posting_date=day,
		shoot_purpose=purpose,
	)


def held(moves):
	return {(h["employee"], h["item_code"]): h for h in net_holdings(moves, SITE)}


class UnitTestHoldings(UnitTestCase):
	def test_check_in_cancels_check_out(self):
		moves = [
			move("A", "Gimbal", 2, date(2026, 11, 2)),
			move("A", "Gimbal", 2, date(2026, 11, 3), out=False),
		]
		self.assertEqual(held(moves), {})

	def test_partial_return_leaves_the_rest_with_the_person(self):
		moves = [
			move("A", "SD card", 3, date(2026, 11, 2)),
			move("A", "SD card", 1, date(2026, 11, 3), out=False),
		]
		self.assertEqual(held(moves)[("A", "SD card")]["qty"], 2)

	def test_several_people_hold_the_same_item(self):
		moves = [move("A", "Mic", 1, date(2026, 11, 2)), move("B", "Mic", 2, date(2026, 11, 2))]
		result = held(moves)
		self.assertEqual(result[("A", "Mic")]["qty"], 1)
		self.assertEqual(result[("B", "Mic")]["qty"], 2)

	def test_since_is_the_start_of_the_current_spell(self):
		moves = [
			move("A", "Camera", 1, date(2026, 10, 1), purpose="Old shoot"),
			move("A", "Camera", 1, date(2026, 10, 2), out=False),
			move("A", "Camera", 1, date(2026, 11, 2), purpose="Heritage Day"),
			move("A", "Camera", 1, date(2026, 11, 3)),
		]
		h = held(moves)[("A", "Camera")]
		self.assertEqual((h["qty"], h["since"], h["purpose"]), (2, date(2026, 11, 2), "Heritage Day"))

	def test_moves_that_do_not_touch_site_are_ignored(self):
		office_to_office = move("A", "Light", 1, date(2026, 11, 2))
		office_to_office.t_warehouse = OFFICE
		self.assertEqual(held([office_to_office]), {})


class IntegrationTestEquipment(IntegrationTestCase):
	def test_employee_cannot_open_the_full_register(self):
		frappe.set_user("Guest")
		self.addCleanup(frappe.set_user, "Administrator")
		self.assertRaises(frappe.PermissionError, get_equipment, "register")

	def test_check_out_must_name_the_champion_and_go_to_site(self):
		settings = frappe.get_single("One Settings")
		if not (settings.check_out_type and settings.office_warehouse and settings.site_warehouse):
			self.skipTest("Check Out is not set up in One Settings")
		# Unsaved, so only the hook runs
		entry = frappe.get_doc(
			{
				"doctype": "Stock Entry",
				"stock_entry_type": settings.check_out_type,
				"items": [{"s_warehouse": settings.office_warehouse, "t_warehouse": settings.site_warehouse}],
			}
		)
		self.assertRaises(frappe.ValidationError, validate_stock_entry, entry)
		entry.asset_champion = "HR-EMP-TEST"
		validate_stock_entry(entry)
		entry.items[0].t_warehouse = settings.office_warehouse
		self.assertRaises(frappe.ValidationError, validate_stock_entry, entry)

from datetime import date

from frappe.tests import UnitTestCase

from asante_one.api.rules import occurrences

# Day of Reconciliation, a Wednesday
HOLIDAYS = {date(2026, 12, 16)}


def dates(start, end, **reminder):
	return occurrences(reminder, start, end, HOLIDAYS)


class UnitTestReminderRules(UnitTestCase):
	def test_weekly(self):
		self.assertEqual(
			dates(date(2026, 11, 4), date(2026, 11, 20), rule="Weekly", weekday="Monday"),
			[date(2026, 11, 9), date(2026, 11, 16)],
		)

	def test_monthly_moves_back_from_a_weekend(self):
		# 7 November 2026 is a Saturday
		self.assertEqual(
			dates(date(2026, 11, 1), date(2026, 11, 30), rule="Monthly on day", day=7), [date(2026, 11, 6)]
		)

	def test_monthly_moves_back_from_a_holiday(self):
		self.assertEqual(
			dates(date(2026, 12, 1), date(2026, 12, 31), rule="Monthly on day", day=16),
			[date(2026, 12, 15)],
		)

	def test_day_31_in_a_short_month_is_the_last_day(self):
		self.assertEqual(
			dates(date(2026, 11, 1), date(2026, 11, 30), rule="Monthly on day", day=31),
			[date(2026, 11, 30)],
		)

	def test_last_business_day_of_month(self):
		# 31 January 2027 is a Sunday
		self.assertEqual(
			dates(date(2027, 1, 1), date(2027, 1, 31), rule="Last business day of month"),
			[date(2027, 1, 29)],
		)

	def test_date_moved_back_from_next_month_is_included(self):
		# 1 May 2027 is a Saturday, so the reminder falls on Friday 30 April
		self.assertEqual(
			dates(date(2027, 4, 20), date(2027, 4, 30), rule="Monthly on day", day=1), [date(2027, 4, 30)]
		)

	def test_yearly(self):
		# EMP501 interim: 31 October 2026 is a Saturday
		self.assertEqual(
			dates(date(2026, 10, 1), date(2027, 9, 30), rule="Yearly on date", day=31, month="October"),
			[date(2026, 10, 30)],
		)

	def test_incomplete_rule_has_no_dates(self):
		self.assertEqual(dates(date(2026, 11, 1), date(2026, 12, 31), rule="Weekly"), [])
		self.assertEqual(dates(date(2026, 11, 1), date(2026, 12, 31), rule="Monthly on day"), [])

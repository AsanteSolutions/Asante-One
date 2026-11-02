"""Department reminders: turn a rule like "monthly on the 7th" into real dates.

A business day is a weekday that is not a holiday in the default Holiday List. Dates that fall
on a day off move back to the business day before, the way SARS deadlines work.
"""

import calendar
from datetime import date, timedelta

import frappe
from frappe.utils import add_days

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
MONTHS = list(calendar.month_name)[1:]

REMINDER_DAYS = 45
REMINDER_COUNT = 5


def days_off(holiday_list, start, end):
	"""Holidays in the list between two dates. Weekends are handled separately, so weekly offs are skipped."""
	if not holiday_list:
		return set()
	return set(
		frappe.get_all(
			"Holiday",
			filters={
				"parenttype": "Holiday List",
				"parent": holiday_list,
				"holiday_date": ("between", [start, end]),
				"weekly_off": 0,
			},
			pluck="holiday_date",
		)
	)


def is_business_day(day, holidays):
	return day.weekday() < 5 and day not in holidays


def previous_business_day(day, holidays):
	while not is_business_day(day, holidays):
		day -= timedelta(days=1)
	return day


def last_day_of_month(year, month):
	return date(year, month, calendar.monthrange(year, month)[1])


def months_between(start, end):
	"""(year, month) from the month of start to the month after end, so dates moved back are not missed."""
	year, month = start.year, start.month
	last = (end.year + 1, 1) if end.month == 12 else (end.year, end.month + 1)
	while (year, month) <= last:
		yield year, month
		year, month = (year + 1, 1) if month == 12 else (year, month + 1)


def occurrences(reminder, start, end, holidays):
	"""Every date the reminder falls on between start and end, inclusive."""
	rule = reminder.get("rule")
	dates = []

	if rule == "Weekly":
		if reminder.get("weekday") not in WEEKDAYS:
			return []
		day = start + timedelta(days=(WEEKDAYS.index(reminder["weekday"]) - start.weekday()) % 7)
		while day <= end:
			dates.append(day)
			day += timedelta(days=7)
		return dates

	for year, month in months_between(start, end):
		if rule == "Monthly on day" and reminder.get("day"):
			day = date(year, month, min(int(reminder["day"]), calendar.monthrange(year, month)[1]))
		elif rule == "Last business day of month":
			day = last_day_of_month(year, month)
		elif rule == "Yearly on date" and reminder.get("day") and reminder.get("month") in MONTHS:
			if MONTHS.index(reminder["month"]) + 1 != month:
				continue
			day = date(year, month, min(int(reminder["day"]), calendar.monthrange(year, month)[1]))
		else:
			continue
		day = previous_business_day(day, holidays)
		if start <= day <= end:
			dates.append(day)
	return sorted(set(dates))


def upcoming(reminders, today, holiday_list, days=REMINDER_DAYS, count=REMINDER_COUNT):
	"""The next date of each reminder, soonest first. A weekly reminder does not crowd out the others."""
	end = add_days(today, days)
	# Look a few days past the end, so a date moved back from just after it still counts
	holidays = days_off(holiday_list, today, add_days(end, 10))
	items = []
	for reminder in reminders:
		dates = occurrences(reminder.as_dict(), today, end, holidays)
		if dates:
			items.append(
				{
					"date": dates[0],
					"title": reminder.title,
					"description": reminder.description,
					"kind": reminder.kind,
				}
			)
	return sorted(items, key=lambda item: item["date"])[:count]

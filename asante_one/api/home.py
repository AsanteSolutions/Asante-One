"""Home in one call: announcements, coming up, pins and recently updated policies."""

import json
from datetime import date

import frappe
from frappe.query_builder.functions import Coalesce
from frappe.utils import add_days, get_datetime, getdate, now_datetime
from frappe.utils.data import strip_html

from asante_one.api.boot import get_content, get_employee

COMING_UP_DAYS = 90
COMING_UP_COUNT = 6


@frappe.whitelist()
def get_home():
	roles = frappe.get_roles()
	settings = frappe.get_cached_doc("One Settings")
	return {
		"announcements": get_announcements(get_employee(), roles),
		"coming_up": get_coming_up(settings, getdate())[:COMING_UP_COUNT],
		"pins": frappe.get_all("One Pin", filters={"user": frappe.session.user}, pluck="pin_key"),
		"recent_policies": get_content(roles)["recent_policies"],
	}


@frappe.whitelist(methods=["POST"])
def mark_announcements_seen(names):
	"""Called when the person closes the pop up, so it does not show again on any device."""
	if isinstance(names, str):
		names = json.loads(names)
	user = frappe.session.user
	for name in names:
		if not frappe.db.exists("One Announcement", name):
			continue
		if frappe.db.exists("One Announcement View", f"{name}:{user}"):
			continue
		frappe.get_doc(
			{
				"doctype": "One Announcement View",
				"announcement": name,
				"user": user,
				"seen_on": now_datetime(),
			}
		).insert(ignore_permissions=True)


@frappe.whitelist(methods=["POST"])
def toggle_pin(key):
	user = frappe.session.user
	if frappe.db.exists("One Pin", f"{user}:{key}"):
		frappe.delete_doc("One Pin", f"{user}:{key}", ignore_permissions=True)
	else:
		frappe.get_doc({"doctype": "One Pin", "user": user, "pin_key": key}).insert(ignore_permissions=True)
	return frappe.get_all("One Pin", filters={"user": user}, pluck="pin_key")


# Announcements


def get_announcements(employee, roles):
	"""Live announcements for this person, urgent first, each flagged with whether they have seen it."""
	rows = frappe.get_all(
		"One Announcement",
		filters={"published": 1, "publish_from": ("<=", now_datetime())},
		or_filters=[["show_until", "is", "not set"], ["show_until", ">=", getdate()]],
		fields=[
			"name",
			"title",
			"priority",
			"body",
			"read_more",
			"publish_from",
			"audience",
			"department",
			"branch",
			"role",
		],
		order_by="publish_from desc",
	)
	rows = [row for row in rows if in_audience(row, employee, roles)]
	# View names are "<announcement>:<user>", so this is a primary key lookup
	user = frappe.session.user
	seen = set(
		frappe.get_all(
			"One Announcement View",
			filters={"name": ("in", [f"{row.name}:{user}" for row in rows])},
			pluck="announcement",
		)
		if rows
		else []
	)
	rows.sort(key=lambda row: row.priority != "Urgent")
	return [
		{
			"name": row.name,
			"title": row.title,
			"urgent": row.priority == "Urgent",
			"body": row.body,
			"read_more": row.read_more,
			"published_on": getdate(row.publish_from),
			"seen": row.name in seen,
		}
		for row in rows
	]


def in_audience(announcement, employee, roles):
	if announcement.audience == "Department":
		return bool(employee) and employee.department == announcement.department
	if announcement.audience == "Branch":
		return bool(employee) and employee.branch == announcement.branch
	if announcement.audience == "Role":
		return announcement.role in roles
	return True


# Coming up


def get_coming_up(settings, today):
	end = add_days(today, COMING_UP_DAYS)
	holidays = get_holidays(settings.holiday_list, today, end)
	items = holidays + get_company_events(
		settings.company_calendar, today, end, {h["date"] for h in holidays}
	)
	if settings.show_birthdays or settings.show_work_anniversaries:
		items += get_celebrations(settings, today, end)
	return sorted(items, key=lambda item: item["date"])


def coming_up_item(day, title, subtitle, kind, label, to=None, person=None):
	return {
		"date": day,
		"title": title,
		"subtitle": subtitle,
		"kind": kind,
		"label": label,
		"to": to,
		"person": person,
	}


def get_holidays(holiday_list, start, end):
	if not holiday_list:
		return []
	rows = frappe.get_all(
		"Holiday",
		filters={
			"parenttype": "Holiday List",
			"parent": holiday_list,
			"holiday_date": ("between", [start, end]),
			"weekly_off": 0,
		},
		fields=["holiday_date", "description"],
		order_by="holiday_date asc",
	)
	return [
		coming_up_item(
			row.holiday_date,
			strip_html(row.description).strip(),
			"Public holiday",
			"public_holiday",
			"Public holiday",
		)
		for row in rows
	]


EVENT_LABELS = {
	"Shutdown": ("closure", "Shutdown"),
	"Closure": ("closure", "Closure"),
	"Company holiday": ("closure", "Company holiday"),
	"Social": ("company", "Company"),
	"Company": ("company", "Company"),
}


def event_category(event):
	if event.one_category:
		return event.one_category
	subject = (event.subject or "").lower()
	if "shutdown" in subject:
		return "Shutdown"
	if "closure" in subject or "closed" in subject:
		return "Closure"
	return "Company"


def get_company_events(company_calendar, start, end, holiday_dates):
	"""Events from the company holiday calendar, plus Desk events given an ASANTE ONE category."""
	Event = frappe.qb.DocType("Event")
	source = Event.one_category.isnotnull() & (Event.one_category != "")
	if company_calendar:
		source = source | (Event.google_calendar == company_calendar)

	events = (
		frappe.qb.from_(Event)
		.select(Event.name, Event.subject, Event.starts_on, Event.ends_on, Event.one_category)
		.where(source)
		.where(Event.status != "Cancelled")
		.where(Event.starts_on <= get_datetime(f"{end} 23:59:59"))
		.where(Coalesce(Event.ends_on, Event.starts_on) >= get_datetime(f"{start} 00:00:00"))
		.orderby(Event.starts_on)
		.run(as_dict=True)
	)

	items = []
	for event in events:
		category = event_category(event)
		first_day = getdate(event.starts_on)
		last_day = getdate(event.ends_on) if event.ends_on else first_day
		# A public holiday on Thithi's calendar is already in the Holiday List
		if category in ("Company", "Company holiday") and first_day in holiday_dates:
			continue
		kind, label = EVENT_LABELS.get(category, EVENT_LABELS["Company"])
		subtitle = f"Until {last_day.strftime('%-d %b')}" if last_day > first_day else None
		items.append(
			coming_up_item(
				max(first_day, start), event.subject, subtitle, kind, label, to=f"/life/{event.name}"
			)
		)
	return items


def next_occurrence(day, today):
	"""The next anniversary of `day` on or after today. 29 February falls on 28 February otherwise."""

	def in_year(year):
		try:
			return day.replace(year=year)
		except ValueError:
			return date(year, 2, 28)

	occurrence = in_year(today.year)
	return occurrence if occurrence >= today else in_year(today.year + 1)


def get_celebrations(settings, start, end):
	employees = frappe.get_all(
		"Employee",
		filters={"status": "Active"},
		fields=["name", "employee_name", "user_id", "date_of_birth", "date_of_joining"],
	)
	images = dict(
		frappe.get_all(
			"User",
			filters={"name": ("in", [e.user_id for e in employees if e.user_id])},
			fields=["name", "user_image"],
			as_list=True,
		)
	)

	items = []
	for employee in employees:
		person = {"name": employee.employee_name, "image": images.get(employee.user_id)}
		if settings.show_birthdays and employee.date_of_birth:
			day = next_occurrence(getdate(employee.date_of_birth), start)
			if day <= end:
				items.append(
					coming_up_item(
						day, employee.employee_name, "Birthday", "birthday", "Birthday", person=person
					)
				)
		if settings.show_work_anniversaries and employee.date_of_joining:
			joined = getdate(employee.date_of_joining)
			day = next_occurrence(joined, start)
			years = day.year - joined.year
			if years >= 1 and day <= end:
				items.append(
					coming_up_item(
						day,
						f"{employee.employee_name}: {years} year{'s' if years > 1 else ''} at Asante Solutions",
						"Work anniversary",
						"anniversary",
						"Anniversary",
						person=person,
					)
				)
	return items

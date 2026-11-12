"""Life at Asante Solutions: the dates list and month, memories of past events, and one event."""

import frappe
from frappe import _
from frappe.utils import date_diff, getdate, now_datetime
from frappe.utils.data import strip_html

from asante_one.api.boot import public_file
from asante_one.api.home import company_events, event_category, get_dates

MAX_RANGE_DAYS = 400
MEMORY_COUNT = 24


@frappe.whitelist()
def get_life(start, end):
	"""Holidays, company events, birthdays and anniversaries between two dates."""
	start, end = getdate(start), getdate(end)
	if end < start or date_diff(end, start) > MAX_RANGE_DAYS:
		frappe.throw(_("Choose a range of at most {0} days").format(MAX_RANGE_DAYS))
	return get_dates(frappe.get_cached_doc("One Settings"), start, end)


@frappe.whitelist()
def get_memories():
	"""Past company events, newest first, with their cover photo and photo folder."""
	Event = frappe.qb.DocType("Event")
	settings = frappe.get_cached_doc("One Settings")
	events = (
		company_events(
			settings.company_calendar, Event.description, Event.cover_image, Event.photo_folder_url
		)
		.where(Event.starts_on < now_datetime())
		.orderby(Event.starts_on, order=frappe.qb.desc)
		.limit(MEMORY_COUNT)
		.run(as_dict=True)
	)
	return [
		{
			"name": e.name,
			"title": e.subject,
			"date": getdate(e.starts_on),
			"category": event_category(e),
			"summary": strip_html(e.description or "").strip()[:160],
			"cover_image": public_file(e.cover_image),
			"photo_folder_url": e.photo_folder_url,
		}
		for e in events
	]


@frappe.whitelist()
def get_event(name):
	"""One company event. Any other Event, such as someone's private meeting, is not found."""
	Event = frappe.qb.DocType("Event")
	settings = frappe.get_cached_doc("One Settings")
	event = (
		company_events(
			settings.company_calendar,
			Event.description,
			Event.all_day,
			Event.cover_image,
			Event.photo_folder_url,
		)
		.where(Event.name == name)
		.run(as_dict=True)
	)
	if not event:
		frappe.throw(_("Event not found"), frappe.DoesNotExistError)
	event = event[0]
	return {
		"name": event.name,
		"title": event.subject,
		"category": event_category(event),
		"starts_on": event.starts_on,
		"ends_on": event.ends_on,
		"all_day": event.all_day,
		"past": (event.ends_on or event.starts_on) < now_datetime(),
		"description": event.description,
		"cover_image": public_file(event.cover_image),
		"photo_folder_url": event.photo_folder_url,
	}

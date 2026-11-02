import hashlib

import frappe

CONTENT_KEY = "asante_one:content"


def for_roles(roles, generator):
	"""Content lists depend only on the role set, so people with the same roles share one entry."""
	key = hashlib.sha1(",".join(sorted(roles)).encode()).hexdigest()
	return frappe.cache.hget(CONTENT_KEY, key, generator=generator)


def clear(doc=None, method=None):
	frappe.cache.delete_value(CONTENT_KEY)

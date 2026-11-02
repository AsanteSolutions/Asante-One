import hashlib

import frappe

CONTENT_KEY = "asante_one:content"


def for_roles(roles, generator):
	"""Content lists depend only on the role set, so people with the same roles share one entry."""
	key = hashlib.sha1(",".join(sorted(roles)).encode()).hexdigest()
	return frappe.cache.hget(CONTENT_KEY, key, generator=generator)


def clear(doc=None, method=None):
	frappe.cache.delete_value(CONTENT_KEY)


def clear_if_photo_changed(doc, method=None):
	"""Who to ask shows people's photos, so a new profile photo refreshes the lists."""
	if doc.has_value_changed("user_image"):
		clear()

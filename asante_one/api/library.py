"""Policies, Drive resources, tools and who to ask, for the People and HR, Policies and How we work pages."""

import frappe

from asante_one.api.boot import get_content


@frappe.whitelist()
def get_library():
	"""Everything those pages list, filtered by role and cached. Restricted resources never reach an employee."""
	return get_content(frappe.get_roles())["library"]


@frappe.whitelist()
def get_policy(name):
	if not frappe.db.exists("One Policy", name):
		frappe.throw(frappe._("Policy not found"), frappe.DoesNotExistError)
	policy = frappe.get_cached_doc("One Policy", name)
	related = [row.policy for row in policy.related]
	titles = (
		{
			row.name: row
			for row in frappe.get_all(
				"One Policy", filters={"name": ("in", related)}, fields=["name", "title", "status"]
			)
		}
		if related
		else {}
	)
	return {
		"name": policy.name,
		"title": policy.title,
		"box": policy.box,
		"status": policy.status,
		"policy_owner": policy.policy_owner,
		"drive_url": policy.drive_url,
		"updated_on": policy.updated_on,
		"next_review": policy.next_review,
		"summary": policy.summary,
		"takeaways": [row.takeaway for row in policy.takeaways],
		"related": [titles[name] for name in related if name in titles],
	}

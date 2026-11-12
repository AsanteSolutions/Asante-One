"""The shell's first paint: who the person is, what they may open, and the search index.

`get_boot` is rendered into one.html on the server, so the SPA starts without a request.
Every list is filtered by role here; a restricted link never reaches the browser.
"""

import frappe
from frappe.utils import get_system_timezone
from frappe.utils.data import strip_html

from asante_one.api import cache

ADMIN_ROLES = {"Asante One Admin", "System Manager"}
CUSTODIAN_ROLE = "Company Assets Custodian"


@frappe.whitelist()
def get_boot():
	roles = frappe.get_roles()
	employee = get_employee()
	content = get_content(roles)
	return {
		"user": get_user(),
		"employee": employee,
		"is_admin": is_admin(roles),
		"is_custodian": is_admin(roles) or CUSTODIAN_ROLE in roles,
		"timezone": get_system_timezone(),
		"links": get_links(employee),
		"hr_actions": content["hr_actions"],
		"quick_actions": get_quick_actions(employee, content["hr_actions"]),
		"search": content["search"] + get_department_search(employee),
		"pins": frappe.get_all("One Pin", filters={"user": frappe.session.user}, pluck="pin_key"),
	}


def check_app_permission():
	"""Show ASANTE ONE on the apps screen to staff, not to website users such as course learners."""
	return frappe.get_cached_value("User", frappe.session.user, "user_type") == "System User"


def is_admin(roles):
	return bool(ADMIN_ROLES.intersection(roles))


def can_see(allowed_roles, roles):
	"""Empty means everyone. Admins see everything so they can check what others see."""
	return not allowed_roles or is_admin(roles) or bool(set(allowed_roles).intersection(roles))


def get_user():
	user = frappe.db.get_value(
		"User", frappe.session.user, ["name", "full_name", "first_name", "user_image"], as_dict=True
	)
	return {
		"name": user.name,
		"full_name": user.full_name or user.name,
		"first_name": user.first_name or user.full_name or user.name,
		"image": user.user_image,
	}


def get_employee():
	employee = frappe.db.get_value(
		"Employee",
		{"user_id": frappe.session.user, "status": "Active"},
		["name", "employee_name", "designation", "department", "branch", "company"],
		as_dict=True,
	)
	if not employee:
		return None
	employee.department_name = (
		frappe.db.get_value("Department", employee.department, "department_name")
		if employee.department
		else None
	)
	return employee


def get_links(employee):
	from asante_one.api.equipment import get_check_links

	settings = frappe.get_cached_doc("One Settings")
	return {
		"desk": "/desk",
		"hrms": "/hrms",
		"clickup": settings.clickup_url,
		"operations_drive": settings.operations_drive_url,
		"incident_template": settings.incident_template_url,
		"purchase_list": settings.purchase_list_url,
		"equipment_process": settings.equipment_process_url,
		**get_check_links(employee),
	}


def get_department_profile(employee):
	if not employee or not employee.department:
		return None
	if not frappe.db.exists("One Department Profile", employee.department):
		return None
	return frappe.get_cached_doc("One Department Profile", employee.department)


def get_department_search(employee):
	"""The person's department toolkit, so search finds their team's tools too."""
	profile = get_department_profile(employee)
	if not profile:
		return []
	group = profile.display_name or employee.department_name
	return [
		{"group": group, "title": t.label, "subtitle": t.subtitle, "kind": "url", "url": t.url}
		for t in profile.tools
		if t.url
	]


def get_quick_actions(employee, hr_actions):
	"""The company wide actions from One Settings, then the person's department actions."""
	hr_by_key = {action["key"]: action for action in hr_actions}
	rows = list(frappe.get_cached_doc("One Settings").quick_actions)
	profile = get_department_profile(employee)
	if profile:
		rows += profile.quick_actions

	actions = []
	for row in rows:
		action = {"label": row.label, "subtitle": row.subtitle, "icon": row.icon}
		if row.action_type == "HR Action":
			# An HR action the person cannot see is dropped, not shown broken
			if row.hr_action not in hr_by_key:
				continue
			action.update(kind="hr", key=row.hr_action)
		elif row.action_type == "Page":
			action.update(kind="page", to=row.page)
		else:
			action.update(kind="url", url=row.url)
		actions.append(action)
	return actions


def get_content(roles):
	return cache.for_roles(roles, lambda: build_content(roles))


def child_roles(parenttype, parentfield):
	roles = {}
	for row in frappe.get_all(
		"One Role",
		filters={"parenttype": parenttype, "parentfield": parentfield},
		fields=["parent", "role"],
	):
		roles.setdefault(row.parent, []).append(row.role)
	return roles


def build_content(roles):
	action_roles = child_roles("One HR Action", "roles")
	hr_actions = [
		{
			"key": row.name,
			"label": row.label,
			"module": row.module,
			"icon": row.icon,
			"desk_route": row.desk_route,
			"mobile_route": row.mobile_route,
			"record": row.record,
			"verified": row.verified,
		}
		for row in frappe.get_all(
			"One HR Action",
			fields=["name", "label", "module", "icon", "desk_route", "mobile_route", "record", "verified"],
			order_by="sequence asc, label asc",
		)
		if can_see(action_roles.get(row.name), roles)
	]

	resource_roles = child_roles("One Resource", "restricted_roles")
	resources = [
		frappe._dict(row, restricted=bool(resource_roles.get(row.name)))
		for row in frappe.get_all(
			"One Resource",
			fields=[
				"name",
				"title",
				"url",
				"category",
				"description",
				"content_owner",
				"who_can_open",
				"featured",
			],
			order_by="title asc",
		)
		if can_see(resource_roles.get(row.name), roles)
	]

	boxes = frappe.get_all(
		"One Policy Box",
		fields=["name", "title", "icon", "drive_folder_url", "drive_folder_name"],
		order_by="sequence asc, title asc",
	)
	policies = frappe.get_all(
		"One Policy",
		fields=[
			"name",
			"title",
			"box",
			"status",
			"policy_owner",
			"drive_url",
			"updated_on",
			"next_review",
			"summary",
		],
		order_by="title asc",
	)
	tools = frappe.get_all(
		"One Tool",
		fields=["tool_name", "purpose", "used_by", "url", "guide_url", "tracked_measures"],
		order_by="sequence asc",
	)
	help_topics = get_help_topics()

	recent_policies = sorted(
		(p for p in policies if p.updated_on and p.status not in ("Missing", "Archived")),
		key=lambda p: p.updated_on,
		reverse=True,
	)[:3]

	return {
		"hr_actions": hr_actions,
		"recent_policies": [
			{"name": p.name, "title": p.title, "status": p.status, "updated_on": p.updated_on}
			for p in recent_policies
		],
		"library": {
			"boxes": boxes,
			"policies": policies,
			"resources": resources,
			"tools": tools,
			"help": help_topics,
		},
		"search": build_search(hr_actions, policies, resources, tools, help_topics),
	}


def get_help_topics():
	"""Who to ask, with each named person's photo from their User profile."""
	topics = frappe.get_all(
		"One Help Topic",
		fields=[
			"name",
			"help_group",
			"question",
			"role",
			"person",
			"person_name",
			"how_to_reach",
			"request_label",
			"request_url",
		],
		order_by="sequence asc",
	)
	people = [t.person for t in topics if t.person]
	users = dict(
		frappe.get_all("Employee", filters={"name": ("in", people)}, fields=["name", "user_id"], as_list=True)
		if people
		else []
	)
	images = photos(users.values())
	for topic in topics:
		topic.person_image = images.get(users.get(topic.person))
		del topic["person"]
	return topics


def photos(users):
	"""Profile photos by User, for showing other people.

	A private photo would not open for them, so it is left out and their initials show instead.
	"""
	users = [u for u in users if u]
	if not users:
		return {}
	return {
		name: image
		for name, image in frappe.get_all(
			"User", filters={"name": ("in", users)}, fields=["name", "user_image"], as_list=True
		)
		if public_file(image)
	}


def public_file(url):
	"""The URL when everyone can open it: not a private file."""
	return url if url and not url.startswith("/private/") else None


def build_search(hr_actions, policies, resources, tools, help_topics):
	"""A flat index the browser searches, like the prototype. A few hundred rows at most."""
	index = []
	for a in hr_actions:
		index.append(
			{
				"group": "Frappe HR",
				"title": a["label"],
				"subtitle": a["module"],
				"kind": "hr",
				"key": a["key"],
			}
		)
	for p in policies:
		index.append(
			{
				"group": "Policies",
				"title": p.title,
				"subtitle": f"{p.box} · {p.status}",
				"kind": "page",
				"to": f"/policies/{p.name}",
			}
		)
	for r in resources:
		index.append(
			{
				"group": "Resources",
				"title": r.title,
				"subtitle": r.description or r.category,
				"kind": "url",
				"url": r.url,
				"restricted": r.restricted,
			}
		)
	for t in tools:
		if t.url:
			index.append(
				{
					"group": "Tools",
					"title": t.tool_name,
					"subtitle": strip_html(t.purpose or ""),
					"kind": "url",
					"url": t.url,
				}
			)
	for h in help_topics:
		index.append(
			{
				"group": "Who to ask",
				"title": h.question,
				"subtitle": " · ".join(filter(None, [h.role, h.person_name])),
				"kind": "page",
				"to": "/how-we-work/who-to-ask",
			}
		)
	return index

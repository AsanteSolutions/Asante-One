"""Equipment: shoot kit is stock that moves between the Office and Site warehouses, personal kit is Assets.

Who has shoot kit comes from the transfers in and out of Site: each names an `asset_champion`, and a
person holds what they checked out less what they checked in. Every query runs here, so an employee
needs no read access to Bin, Stock Entry or Asset. The full register is for the custodian and admins.
"""

from urllib.parse import urlencode

import frappe
from frappe import _
from frappe.query_builder import DocType
from frappe.query_builder.functions import Sum

from asante_one.api.boot import CUSTODIAN_ROLE, get_employee, is_admin, photos, public_file

TABS = ("mine", "kit", "out", "register")
RECENT_COUNT = 15


@frappe.whitelist()
def get_equipment(tab="mine"):
	roles = frappe.get_roles()
	if tab not in TABS:
		tab = "mine"
	if tab == "register" and not is_custodian(roles):
		frappe.throw(
			_("Only the Company Assets Custodian can open the full register"), frappe.PermissionError
		)

	settings = get_settings()
	employee = get_employee()
	data = {"tab": tab, "configured": bool(settings)}

	# Personal kit does not depend on the stock setup, so My equipment lists it either way
	if tab == "mine":
		data["assets"] = get_assets({"custodian": employee.name}) if employee else []
	if not settings:
		return data

	stock = get_stock(settings)
	if tab == "kit":
		data["items"] = list(stock.values())
	elif tab == "mine":
		data["kit"] = (
			[h for h in get_holdings(settings, stock) if h["employee"] == employee.name] if employee else []
		)
	elif tab == "out":
		data.update(get_out(settings, stock))
	else:
		data.update(get_register(settings, stock))
	return data


def is_custodian(roles):
	return is_admin(roles) or CUSTODIAN_ROLE in roles


def get_settings():
	"""One Settings when the Check Out and Check In types and both warehouses are set, otherwise None."""
	settings = frappe.get_cached_doc("One Settings")
	required = (
		settings.check_out_type,
		settings.check_in_type,
		settings.office_warehouse,
		settings.site_warehouse,
	)
	return settings if all(required) else None


def get_check_links(employee):
	"""New Check Out and Check In entries in Desk, with the type and the person filled in.

	Desk does not copy the warehouses from the address (they are no_copy), so the Stock Entry form
	script fills them in from the type.
	"""
	settings = get_settings()
	if not settings:
		return {}

	def new_entry(entry_type):
		params = {"stock_entry_type": entry_type}
		if employee:
			params["asset_champion"] = employee.name
		return "/desk/stock-entry/new?" + urlencode(params)

	return {"check_out": new_entry(settings.check_out_type), "check_in": new_entry(settings.check_in_type)}


def extend_bootinfo(bootinfo):
	"""Where each type moves kit, for `public/js/stock_entry.js`."""
	settings = get_settings()
	if settings:
		office, site = settings.office_warehouse, settings.site_warehouse
		bootinfo.asante_one_check_types = {
			settings.check_out_type: {"from": office, "to": site},
			settings.check_in_type: {"from": site, "to": office},
		}


def validate_stock_entry(doc, method=None):
	"""Check Out and Check In move kit one way between the office and site, and say who has it."""
	settings = get_settings()
	if not settings or doc.stock_entry_type not in (settings.check_out_type, settings.check_in_type):
		return
	if doc.stock_entry_type == settings.check_out_type:
		source, target = settings.office_warehouse, settings.site_warehouse
	else:
		source, target = settings.site_warehouse, settings.office_warehouse
	if not doc.asset_champion:
		frappe.throw(
			_("Name the asset champion: the person taking the kit out, or whose kit is coming back."),
			title=_("Who has the kit?"),
		)
	for row in doc.items:
		if row.s_warehouse != source or row.t_warehouse != target:
			frappe.throw(
				_("Row {0}: {1} moves kit from {2} to {3}.").format(
					row.idx, doc.stock_entry_type, source, target
				),
				title=_("Wrong warehouse"),
			)


def get_stock(settings):
	"""Every stock item with kit in the office or out on site, keyed by item code."""
	office, site = settings.office_warehouse, settings.site_warehouse
	bins = frappe.get_all(
		"Bin",
		filters={"warehouse": ("in", (office, site)), "actual_qty": ("!=", 0)},
		fields=["item_code", "warehouse", "actual_qty"],
	)
	if not bins:
		return {}
	items = {
		row.name: {
			"item_code": row.name,
			"item_name": row.item_name,
			"item_group": row.item_group,
			"image": public_file(row.image),
			"available": 0,
			"out": 0,
		}
		for row in frappe.get_all(
			"Item",
			filters={"name": ("in", list({b.item_code for b in bins})), "disabled": 0},
			fields=["name", "item_name", "item_group", "image"],
			order_by="item_group asc, item_name asc",
		)
	}
	for b in bins:
		if b.item_code in items:
			items[b.item_code]["available" if b.warehouse == office else "out"] += b.actual_qty
	return items


def get_holdings(settings, stock):
	"""What each person has out on site, with the item details. Kit no longer on site is left out."""
	SE, SED = DocType("Stock Entry"), DocType("Stock Entry Detail")
	site = settings.site_warehouse
	moves = (
		frappe.qb.from_(SED)
		.join(SE)
		.on(SE.name == SED.parent)
		.select(
			SE.asset_champion,
			SED.item_code,
			SED.s_warehouse,
			SED.t_warehouse,
			SED.transfer_qty,
			SE.posting_date,
			SE.shoot_purpose,
		)
		.where(
			(SE.docstatus == 1)
			& (SE.purpose == "Material Transfer")
			& (SE.asset_champion.isnotnull())
			& (SE.asset_champion != "")
			& ((SED.s_warehouse == site) | (SED.t_warehouse == site))
		)
		.orderby(SE.posting_date)
		.orderby(SE.posting_time)
		.orderby(SE.creation)
		.run(as_dict=True)
	)
	holdings = [
		{**h, **{k: stock[h["item_code"]][k] for k in ("item_name", "item_group", "image")}}
		for h in net_holdings(moves, site)
		if stock.get(h["item_code"], {}).get("out", 0) > 0
	]
	people = get_people({h["employee"] for h in holdings})
	for h in holdings:
		person = people.get(h["employee"], {})
		h["employee_name"] = person.get("name") or h["employee"]
		h["employee_image"] = person.get("image")
	return holdings


def net_holdings(moves, site):
	"""Per person and item, the quantity moved into site less the quantity moved back out.

	`moves` are transfer rows in posting order. `since` is when the person's current spell with the
	item began, and `purpose` is from their latest check out.
	"""
	held = {}
	for move in moves:
		sign = (move.t_warehouse == site) - (move.s_warehouse == site)
		if not sign:
			continue
		key = (move.asset_champion, move.item_code)
		h = held.setdefault(key, {"qty": 0, "since": None, "purpose": None})
		if sign > 0:
			if h["qty"] <= 0:
				h["since"] = move.posting_date
			h["purpose"] = move.shoot_purpose or h["purpose"]
		h["qty"] += sign * move.transfer_qty
	return [
		{"employee": employee, "item_code": item_code, **h}
		for (employee, item_code), h in held.items()
		if h["qty"] > 0
	]


def get_out(settings, stock):
	"""Kit on site grouped by who has it, then whatever on site no check out names anyone for."""
	named = {}
	by_person = {}
	for h in get_holdings(settings, stock):
		named[h["item_code"]] = named.get(h["item_code"], 0) + h["qty"]
		person = by_person.setdefault(
			h["employee"],
			{
				"employee": h["employee"],
				"name": h["employee_name"],
				"image": h["employee_image"],
				"items": [],
			},
		)
		person["items"].append(h)
	unnamed = [
		{**item, "qty": item["out"] - named.get(code, 0)}
		for code, item in stock.items()
		if item["out"] - named.get(code, 0) > 0
	]
	return {"people": sorted(by_person.values(), key=lambda p: p["name"]), "unnamed": unnamed}


def get_register(settings, stock):
	out = get_out(settings, stock)
	holders = {}
	for person in out["people"]:
		for h in person["items"]:
			holders.setdefault(h["item_code"], []).append({"name": person["name"], "qty": h["qty"]})
	items = [{**item, "holders": holders.get(code, [])} for code, item in stock.items()]
	assets = get_assets({})
	return {
		"items": items,
		"assets": assets,
		"unnamed": out["unnamed"],
		"recent": get_recent(settings),
		"totals": {
			"items": len(items),
			"available": sum(max(item["available"], 0) for item in items),
			"out": sum(max(item["out"], 0) for item in items),
			"unnamed": sum(item["qty"] for item in out["unnamed"]),
			"assets": len(assets),
			"unassigned": sum(1 for a in assets if not a["custodian"]),
		},
	}


def get_recent(settings):
	"""The latest check outs and check ins, so the custodian can spot one with nobody named."""
	types = {settings.check_out_type: "Check out", settings.check_in_type: "Check in"}
	entries = frappe.get_all(
		"Stock Entry",
		filters={"docstatus": 1, "stock_entry_type": ("in", list(types))},
		fields=["name", "stock_entry_type", "posting_date", "asset_champion_name", "shoot_purpose"],
		order_by="posting_date desc, posting_time desc, creation desc",
		limit=RECENT_COUNT,
	)
	if not entries:
		return []
	SED = DocType("Stock Entry Detail")
	quantities = dict(
		frappe.qb.from_(SED)
		.select(SED.parent, Sum(SED.transfer_qty))
		.where(SED.parent.isin([e.name for e in entries]))
		.groupby(SED.parent)
		.run()
	)
	return [
		{
			"name": e.name,
			"kind": types[e.stock_entry_type],
			"posting_date": e.posting_date,
			"champion": e.asset_champion_name,
			"purpose": e.shoot_purpose,
			"qty": quantities.get(e.name, 0),
		}
		for e in entries
	]


def get_assets(filters):
	"""Personal kit in use: Assets not sold, scrapped or cancelled, with each custodian's name."""
	assets = frappe.get_all(
		"Asset",
		filters={"docstatus": ("<", 2), "status": ("not in", ("Sold", "Scrapped")), **filters},
		fields=[
			"name",
			"asset_name",
			"item_name",
			"asset_category",
			"location",
			"custodian",
			"status",
			"image",
		],
		order_by="asset_name asc",
	)
	people = get_people({a.custodian for a in assets if a.custodian})
	for asset in assets:
		asset.image = public_file(asset.image)
		asset.custodian_name = people.get(asset.custodian, {}).get("name")
	return assets


def get_people(employees):
	"""Name and profile photo for each Employee, keyed by Employee ID."""
	if not employees:
		return {}
	rows = frappe.get_all(
		"Employee", filters={"name": ("in", list(employees))}, fields=["name", "employee_name", "user_id"]
	)
	images = photos(r.user_id for r in rows)
	return {r.name: {"name": r.employee_name, "image": images.get(r.user_id)} for r in rows}

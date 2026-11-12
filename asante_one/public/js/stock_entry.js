// Check Out and Check In always move kit between the same two warehouses, so choosing the type
// fills them in. ASANTE ONE's buttons open a new entry with the type already chosen.
frappe.ui.form.on("Stock Entry", {
	refresh(frm) {
		if (frm.is_new()) fill_warehouses(frm);
	},
	stock_entry_type(frm) {
		fill_warehouses(frm);
	},
});

function fill_warehouses(frm) {
	const route = (frappe.boot.asante_one_check_types || {})[frm.doc.stock_entry_type];
	if (!route || frm.doc.docstatus !== 0) return;
	if (frm.doc.from_warehouse !== route.from) frm.set_value("from_warehouse", route.from);
	if (frm.doc.to_warehouse !== route.to) frm.set_value("to_warehouse", route.to);
}

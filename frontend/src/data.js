import { createResource } from "frappe-ui"

/** Policies, Drive resources, tools and who to ask. Loaded once, shared by every page that lists them. */
export const library = createResource({ url: "asante_one.api.library.get_library" })

export function loadLibrary() {
	if (!library.data && !library.loading) library.fetch()
	return library
}

// Policy status tags. "Missing" reads as "Not in Drive yet", as in the prototype.
export const STATUS = {
	Approved: { label: "Approved", class: "bg-ok-bg text-ok" },
	Draft: { label: "Draft", class: "bg-warn-bg text-warn" },
	"Under review": { label: "Under review", class: "bg-warn-bg text-warn" },
	"Status to verify": { label: "Status to verify", class: "border border-line bg-sunk text-ink-2" },
	Missing: { label: "Not in Drive yet", class: "bg-risk-bg text-risk" },
	Legislation: { label: "Legislation", class: "border border-line bg-sunk text-ink-2" },
	Archived: { label: "Archived", class: "bg-sunk text-grey" },
}

// The same colours as dots in the month view on phones
export const DOTS = {
	public_holiday: "bg-ph",
	company: "bg-ok",
	closure: "bg-ink",
	birthday: "bg-accent",
	anniversary: "bg-accent",
}

// Tag colours for each kind of date
export const KINDS = {
	public_holiday: "bg-ph-bg text-ph",
	company: "bg-ok-bg text-ok",
	closure: "bg-plum text-white",
	birthday: "bg-lav text-accent",
	anniversary: "bg-lav text-accent",
}

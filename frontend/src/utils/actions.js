import { hrAction } from "@/boot"

// The prototype's phone breakpoint. Phones open Frappe HR's mobile app when the action has a route there.
const phone = window.matchMedia("(max-width: 860px)")

export function hrHref(action) {
	const route = (phone.matches && action.mobile_route) || action.desk_route
	return encodeURI(route)
}

/** Where a quick action or search result goes: a router location, or an href to open in a new tab. */
export function resolveAction(item) {
	if (item.kind === "page") return { to: item.to }
	if (item.kind === "hr") {
		const action = hrAction(item.key)
		return action ? { href: hrHref(action) } : null
	}
	return item.url ? { href: item.url } : null
}

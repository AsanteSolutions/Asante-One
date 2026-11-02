export const NAV = [
	{ icon: "home", label: "Home", to: "/" },
	{ icon: "people", label: "People and HR", to: "/hr" },
	{ icon: "book", label: "Policies", to: "/policies" },
	{ icon: "spark", label: "Life at Asante Solutions", to: "/life" },
	{ icon: "map", label: "How we work", to: "/how-we-work" },
	{ icon: "camera", label: "Equipment", to: "/equipment" },
]

// Admins manage content in Desk; this is the only admin entry in the SPA
export const MANAGE_CONTENT = { icon: "gear", label: "Manage content", href: "/desk/asante-one" }

export const TABS = [
	{ icon: "home", label: "Home", to: "/" },
	{ icon: "people", label: "HR", to: "/hr" },
	{ icon: "book", label: "Policies", to: "/policies" },
	{ icon: "spark", label: "Life", to: "/life" },
	{ icon: "grid", label: "More", to: "/more" },
]

export function isActive(route, to) {
	return to === "/" ? route.path === "/" : route.path.startsWith(to)
}

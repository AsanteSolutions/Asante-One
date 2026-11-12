import { ref } from "vue"

const KEY = "one-theme"
const system = window.matchMedia("(prefers-color-scheme: dark)")

function stored() {
	try {
		return localStorage.getItem(KEY)
	} catch {
		return null
	}
}

export const isDark = ref(stored() ? stored() === "dark" : system.matches)

// The phone's status bar follows the chosen theme, not only the system one
function setThemeColour() {
	const colour = getComputedStyle(document.documentElement).getPropertyValue("--canvas").trim()
	document.querySelectorAll('meta[name="theme-color"]').forEach((meta) => meta.setAttribute("content", colour))
}
if (stored()) setThemeColour()

export function toggleTheme() {
	isDark.value = !isDark.value
	const theme = isDark.value ? "dark" : "light"
	document.documentElement.setAttribute("data-theme", theme)
	setThemeColour()
	try {
		localStorage.setItem(KEY, theme)
	} catch {
		// Private windows can refuse storage; the choice then lasts for this page only
	}
}

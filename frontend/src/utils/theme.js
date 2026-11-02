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

export function toggleTheme() {
	isDark.value = !isDark.value
	const theme = isDark.value ? "dark" : "light"
	document.documentElement.setAttribute("data-theme", theme)
	try {
		localStorage.setItem(KEY, theme)
	} catch {
		// Private windows can refuse storage; the choice then lasts for this page only
	}
}

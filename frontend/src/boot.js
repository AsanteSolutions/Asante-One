import { reactive } from "vue"
import { call } from "frappe-ui"

// Filled from window.one, which one.py renders into the page. The Vite dev server has no
// server render, so there it is fetched instead.
export const boot = reactive({ loaded: false })

export async function loadBoot() {
	const data = window.one || (await call("asante_one.api.boot.get_boot"))
	Object.assign(boot, data, { loaded: true })
	return boot
}

export function hrAction(key) {
	return boot.hr_actions.find((action) => action.key === key)
}

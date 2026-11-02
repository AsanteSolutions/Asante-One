import { boot } from "@/boot"

// Every date and time is shown in South African time, whatever the device's time zone.
const zone = () => boot.timezone || "Africa/Johannesburg"

const part = (options) => (date) => new Intl.DateTimeFormat("en-ZA", { timeZone: zone(), ...options }).format(date)

export const clock = part({ hour: "2-digit", minute: "2-digit", hourCycle: "h23" })
export const longDate = part({ weekday: "long", day: "numeric", month: "long", year: "numeric" })
const hourOf = part({ hour: "numeric", hourCycle: "h23" })

export function greeting(now = new Date()) {
	const hour = Number(hourOf(now))
	return hour < 12 ? "Good morning" : hour < 17 ? "Good afternoon" : "Good evening"
}

/** Today in South Africa as YYYY-MM-DD, to compare with the server's dates. */
export function todayISO(now = new Date()) {
	return new Intl.DateTimeFormat("en-CA", { timeZone: zone() }).format(now)
}

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
const DAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

/** Server dates are plain YYYY-MM-DD; read them as calendar days, not instants. */
export function parts(iso) {
	const [y, m, d] = iso.split("-").map(Number)
	const day = new Date(Date.UTC(y, m - 1, d))
	return { day: d, month: MONTHS[m - 1], weekday: DAYS[day.getUTCDay()] }
}

export function shortDay(iso) {
	const p = parts(iso)
	return `${p.weekday} ${p.day} ${p.month}`
}

/** 14 Oct 2026 */
export function formatDate(iso) {
	if (!iso) return ""
	const p = parts(iso)
	return `${p.day} ${p.month} ${iso.slice(0, 4)}`
}

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

const LONG_MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

const fromISO = (iso) => {
	const [y, m, d] = iso.split("-").map(Number)
	return new Date(Date.UTC(y, m - 1, d))
}
const toISO = (date) => date.toISOString().slice(0, 10)

export function addDays(iso, days) {
	const date = fromISO(iso)
	date.setUTCDate(date.getUTCDate() + days)
	return toISO(date)
}

/** "November 2026" for a YYYY-MM month */
export function monthTitle(month) {
	const [y, m] = month.split("-").map(Number)
	return `${LONG_MONTHS[m - 1]} ${y}`
}

export function shiftMonth(month, by) {
	const [y, m] = month.split("-").map(Number)
	return toISO(new Date(Date.UTC(y, m - 1 + by, 1))).slice(0, 7)
}

/** The weeks shown for a month, Monday first, as rows of YYYY-MM-DD including the days around it. */
export function monthWeeks(month) {
	const first = fromISO(`${month}-01`)
	const start = addDays(`${month}-01`, -((first.getUTCDay() + 6) % 7))
	const weeks = []
	let day = start
	do {
		const week = []
		for (let i = 0; i < 7; i++) {
			week.push(day)
			day = addDays(day, 1)
		}
		weeks.push(week)
	} while (day.slice(0, 7) === month)
	return weeks
}

/** 9:00, or nothing for an all day event */
export function timeOf(datetime) {
	return datetime ? datetime.slice(11, 16) : ""
}

/** Whole days from one YYYY-MM-DD to another */
export function daysBetween(from, to) {
	return Math.round((fromISO(to) - fromISO(from)) / 86_400_000)
}

// Smoke tests at phone width: every page renders without sideways scrolling or errors, HR and
// equipment buttons carry the right links, and an employee cannot reach admin content.
//
//   ONE_URL=http://localhost:8000 ONE_EMPLOYEE=user:password ONE_ADMIN=Administrator:admin node tests/smoke.mjs
//
// ONE_EMPLOYEE_SID or ONE_ADMIN_SID can stand in for a password on a local site. The admin run is
// skipped when neither is given. CHROMIUM_PATH points at a browser other than Playwright's own.
import { chromium } from "playwright-core"

const BASE = process.env.ONE_URL || "http://localhost:8000"
const ROUTES = [
	"/",
	"/hr",
	"/policies",
	"/life",
	"/life?view=month",
	"/how-we-work/sops",
	"/how-we-work/tools",
	"/how-we-work/who-to-ask",
	"/how-we-work/request-desk",
	"/equipment",
	"/equipment/kit",
	"/equipment/out",
	"/more",
	"/no-such-page",
]

const failures = []
const check = (ok, message) => {
	console.log(`${ok ? "ok  " : "FAIL"} ${message}`)
	if (!ok) failures.push(message)
}

const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || undefined })

async function signIn(who) {
	const login = process.env[`ONE_${who}`]
	const sid = process.env[`ONE_${who}_SID`]
	if (!login && !sid) return null
	const ctx = await browser.newContext({ baseURL: BASE, viewport: { width: 390, height: 844 } })
	if (sid) {
		await ctx.addCookies([{ name: "sid", value: sid, url: BASE }])
	} else {
		const [usr, ...pwd] = login.split(":")
		const response = await ctx.request.post("/api/method/login", { form: { usr, pwd: pwd.join(":") } })
		check(response.ok(), `${who.toLowerCase()} signs in`)
	}
	return ctx
}

async function open(page, path) {
	const errors = []
	const onError = (e) => errors.push(String(e))
	page.on("pageerror", onError)
	await page.goto("/one" + path, { waitUntil: "networkidle" })
	await page.waitForTimeout(500)
	page.off("pageerror", onError)
	return errors
}

const employee = await signIn("EMPLOYEE")
if (!employee) {
	console.error("Set ONE_EMPLOYEE=user:password (or ONE_EMPLOYEE_SID)")
	process.exit(2)
}
const page = await employee.newPage()

// Every page at 390 pixels, plus the first policy
await open(page, "/policies")
const policy = await page.locator('main a[href^="/one/policies/"]').first().getAttribute("href").catch(() => null)
for (const path of [...ROUTES, ...(policy ? [policy.replace("/one", "")] : [])]) {
	const errors = await open(page, path)
	const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth)
	const heading = await page.locator("main h1, main b").first().isVisible().catch(() => false)
	check(heading && overflow <= 0 && !errors.length, `${path} renders at 390px${overflow > 0 ? `, ${overflow}px too wide` : ""}${errors.length ? `, ${errors[0]}` : ""}`)
}

// HR buttons open the phone route when there is one, otherwise the desk route
await open(page, "/hr")
const { expected, found } = await page.evaluate(() => ({
	expected: window.one.hr_actions.map((a) => encodeURI(a.mobile_route || a.desk_route)),
	found: [...document.querySelectorAll("main a")].map((a) => a.getAttribute("href")),
}))
check(expected.length > 0, "HR actions are listed")
const missing = expected.filter((href) => !found.includes(href))
check(!missing.length, `every HR action links to its route${missing.length ? `; missing ${missing.join(", ")}` : ""}`)

// Equipment buttons open a new Stock Entry of the right type, or the page says it is not set up
await open(page, "/equipment/kit")
const links = await page.evaluate(() => window.one.links)
if (links.check_out) {
	const out = await page.getByRole("link", { name: "Check out" }).getAttribute("href")
	const back = await page.getByRole("link", { name: "Check in" }).getAttribute("href")
	check(out === links.check_out && out.startsWith("/desk/stock-entry/new?stock_entry_type="), "Check out opens a new Check Out entry")
	check(back === links.check_in && back.startsWith("/desk/stock-entry/new?stock_entry_type="), "Check in opens a new Check In entry")
} else {
	check(await page.getByText("Equipment is not set up yet").isVisible(), "Equipment says it is not set up")
}

// Admin content stays out of reach, even by typing the address
check(!(await page.evaluate(() => window.one.is_admin)), "employee is not an admin")
await open(page, "/equipment/register")
check(!(await page.getByRole("link", { name: "Full register" }).count()), "employee has no Full register tab")
await open(page, "/more")
check(!(await page.getByRole("link", { name: "Manage content" }).count()), "employee has no Manage content link")
for (const url of [
	"/api/method/asante_one.api.equipment.get_equipment?tab=register",
	"/api/resource/One Settings/One Settings",
	"/api/resource/One Announcement",
]) {
	const response = await employee.request.get(url)
	check(response.status() === 403, `employee is refused ${url} (${response.status()})`)
}

// The admin sees what the employee does not
const admin = await signIn("ADMIN")
if (admin) {
	const adminPage = await admin.newPage()
	await open(adminPage, "/more")
	check((await adminPage.getByRole("link", { name: "Manage content" }).count()) > 0, "admin has the Manage content link")
	await open(adminPage, "/equipment")
	check((await adminPage.getByRole("link", { name: "Full register" }).count()) > 0, "admin has the Full register tab")
} else {
	console.log("skip admin checks: set ONE_ADMIN or ONE_ADMIN_SID")
}

await browser.close()
console.log(failures.length ? `\n${failures.length} failed` : "\nAll smoke tests passed")
process.exit(failures.length ? 1 : 0)

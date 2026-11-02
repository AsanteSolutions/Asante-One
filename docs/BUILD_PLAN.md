# ASANTE ONE build plan

| | |
|---|---|
| App | `asante_one`, a custom Frappe app on erp.asantepower.co.za |
| Builder | Apile Tyumre |
| Source documents | ASANTE ONE build brief (prototype version 6, 27 Oct 2026); prototype artifact |
| Stack on the bench | Frappe v16.10, ERPNext v16.52, HRMS v16.52, `za_local` |
| Lead time | Three weeks from handover, weekly check in with Thithi, Muhle and Luthando |
| Status | Planning, 30 Oct 2026 |

ASANTE ONE is the front door for Asante Solutions employees. It organises information and sends people to the system that owns the work. It does not store operational records.

---

## 1. Findings that shape the design

These come from checking the brief against the bench and the local site (`asante.localhost`). Confirm the equipment findings against production before acting on them.

| Finding | Design decision |
|---|---|
| ERPNext **Holiday List** already generates South African holidays ("Add local holidays", country ZA, using the `holidays` library). HRMS uses it for leave. | The Holiday List is the single holiday source. Do not port the prototype's Easter and public holiday code. Admins add proclaimed days (for example 4 Nov 2026) as rows. The hub and leave calculations then always agree. |
| Frappe's **Google Calendar** integration can pull a calendar into the `Event` DocType with `sync_as_public`. | The company holiday calendar needs no custom OAuth code. Thithi owns it and connects it once; the hub reads public `Event` rows. |
| **Employee** already holds `date_of_birth`, `date_of_joining`, `department` and `branch`; **User** holds `user_image`, which each person uploads on their own profile. HRMS already sends birthday reminders. | Birthdays and anniversaries come from Employee, not from a Google birthdays calendar. Birthdays are already celebrated company wide, so every active employee is shown and no consent field is needed. Photos come from the linked User's `user_image`, so people choose their own and no photo consent field is needed either; anyone without one gets initials. |
| Frappe v16 has `add_to_apps_screen` and a **Default App** setting at system and user level (see `hrms/hooks.py`). | Landing on ASANTE ONE after login is configuration, not a custom redirect. |
| Equipment on the local site: check out is mostly logged as **Material Issue** ("To Site"), returns as **Material Receipt** ("Return From Site"). The single "From Office To Site" entry has its warehouses reversed. No item is serialised. 51 items exist in ERPNext against 197 rows in the asset register sheet. | Stock balances cannot currently show what is out or who has it. The model must be agreed with Lindo before the Equipment page is built (section 6). |

---

## 2. Architecture

One Frappe app on the existing site, with two surfaces.

```
                    erp.asantepower.co.za  (one site, one login, one DB)
 ┌──────────────────────────────────────────────────────────────────────────┐
 │  /one/*  ── Vue 3 SPA (employees, phone first, PWA)                      │
 │     │  session cookie + CSRF, calls whitelisted methods only             │
 │     ▼                                                                    │
 │  asante_one.api.*  ── read-only aggregation layer, permission filtered,  │
 │     │                 cached in Redis, invalidated on doc save           │
 │     ├── One * DocTypes (announcements, policies, links, tools, help…)    │
 │     ├── HRMS: Employee, Holiday List, (leave balance, later)             │
 │     ├── ERPNext: Item, Bin, Stock Entry, Asset (equipment)               │
 │     └── Frappe: Event (filled by Google Calendar sync, sync_as_public)   │
 │                                                                          │
 │  /desk/asante-one ── Desk workspace (admins): "Manage content" is the    │
 │                      DocType list views. No admin UI in the SPA.         │
 └──────────────────────────────────────────────────────────────────────────┘
   Outbound links only: /desk/* and /hrms (HR), Stock Entry (equipment),
   Google Drive, ClickUp, Metricool, Xero and other tools.
```

Two principles keep this inside three weeks:

1. **Admin screens are Desk, not SPA.** The brief asks for simple Frappe forms that Thithi can update without code. DocType forms in an "Asante One" workspace are exactly that.
2. **The SPA is read only.** The only writes are marking an announcement as seen and pinning a tool.

---

## 3. Technology

| Layer | Choice | Reason |
|---|---|---|
| Backend | Python 3.14, Frappe v16 DocTypes and `@frappe.whitelist` methods | Permissions, cache, scheduler and fixtures come with the framework |
| Frontend | Vue 3, Vite, frappe-ui, Vue Router, served at `/one` | Same pattern as `/hrms`, Helpdesk and CRM; `createResource` handles session and CSRF |
| Styling | Tailwind, with the prototype's CSS variables (`--canvas`, `--accent` and so on) mapped into the theme; light and dark via `data-theme` | Keeps the prototype's look. frappe-ui is used for behaviour (dialogs, dropdowns), not its default skin |
| Fonts and icons | Bricolage Grotesque and Hanken Grotesk self hosted in `public/`; prototype SVG icons as a small component (or Lucide) | No Google Fonts call; works offline |
| PWA | `vite-plugin-pwa`, as HRMS uses | "Add to home screen" so Check out and Check in are two taps on location |
| Tests | `FrappeTestCase` for API and permissions; Playwright smoke tests at 390px | Covers the permission and mobile acceptance tests |

Scaffold the SPA from the frappe-ui starter (doppio's `bench add-spa`, or copy the setup in `apps/hrms/frontend`). Pin a frappe-ui version compatible with v16 rather than reusing HRMS's older 0.1.105. Check the current starter before choosing.

---

## 4. App layout

```
asante_one/
  hooks.py                 # add_to_apps_screen, website_route_rules, doc_events (cache bust), fixtures
  asante_one/doctype/      # One * DocTypes (module "Asante One")
  asante_one/workspace/    # "Asante One" Desk workspace for admins
  api/
    boot.py                # get_boot(): user, employee, nav, settings, search index
    home.py                # get_home(): one aggregate call for Home
    content.py             # policies, life and events, how we work
    equipment.py           # kit availability, my equipment
    rules.py               # reminder rule engine and business day helpers (uses Holiday List)
  www/one.py, one.html     # SPA entry (same pattern as hrms/www/hrms.py: csrf + boot)
  fixtures/                # Custom Fields, Stock Entry Types, Roles, workspace
frontend/                  # Vite app, builds into asante_one/public/frontend
package.json               # "build": "cd frontend && yarn build" so `bench build` runs it
docs/                      # this plan, runbook
```

Hooks:

```python
website_route_rules = [{"from_route": "/one/<path:app_path>", "to_route": "one"}]

add_to_apps_screen = [
	{
		"name": "asante_one",
		"logo": "/assets/asante_one/images/logo.svg",
		"title": "ASANTE ONE",
		"route": "/one",
	}
]
```

Then set **System Settings › Default App = asante_one**. This happens at launch, after testing, not before.

---

## 5. Data model

All new DocTypes live in the "Asante One" module. None of these names clash with anything on the bench.

| DocType | Kind | Key fields |
|---|---|---|
| **One Settings** | Single | default Holiday List; company holiday calendar (Link Google Calendar); incident template URL; purchase list URL; equipment process URL; Check Out and Check In Stock Entry Types; store and site warehouses; ClickUp URL; feature flags |
| **One HR Action** | child of Settings, or standalone | label, module, desk route, mobile route (`/hrms/...`), icon, roles, verified (Check), note. Routes as data, so a wrong route is fixed without a deploy |
| **One Announcement** | normal | title, body (Text Editor), priority (Normal or Urgent), audience (All, Department, Branch, Role), publish_from, show_until, published |
| **One Announcement View** | log | announcement, user, seen_on; unique on (announcement, user). Makes "pops up once per employee" true across devices |
| **One Policy Box** | normal | title, icon, drive_folder_url, sequence |
| **One Policy** | normal | title, box, owner, status (Draft, Under review, Approved, Archived, Missing, Legislation), drive_url, updated_on, next_review, summary, takeaways (child), related (child) |
| **One Resource** | normal | title, url, category (SOPs, Templates, Brand, Admin), owner, description, restricted_roles (Table MultiSelect of Role), featured |
| **One Tool** | normal | name, purpose, used by, url, guide_url, tracked measures |
| **One Help Topic** | normal | group, question, role, person (Link Employee), how to reach (optional), sequence. Every topic names a person. Named so far: Thithi (Growth and People), Muhle (Managing Director), Lindokuhle Nyawo (Company Assets Custodian), Luthando (Technical Lead), Wandile (Finance Lead), Khotso (Client Success Lead). A topic with a request name and "where requests go" link is also listed on the Request desk |
| **One Department Profile** | normal | department (Link Department); tools (child); quick actions (child: label, icon, action type URL, HR Action or route); reminders (child: title, rule, description, kind). Client Success is part of Operations, so its tools and reminders sit in the Operations profile |
| **One Pin** | normal, owner scoped | user, key. Replaces the prototype's browser storage pins |

Custom fields (shipped as fixtures):

- **Event:** `cover_image`, `photo_folder_url`, `one_category` (for example shutdown, closure, company holiday, social)
- **Stock Entry:** `asset_champion` (Link Employee), `shoot_purpose`, alongside the existing `custom_submitted_by`

### Reminder rule engine (`rules.py`)

Rules: weekly on a weekday; monthly on day N, moved back to the previous business day; last business day of the month; yearly on a date. A business day excludes weekends and dates in the default Holiday List.

This covers EMP201 (the 7th), EMP501 (31 October and 31 May), month end close and the weekly rhythms without hard coding any department.

---

## 6. Integrations

### Frappe HR

- Each HR action stores a desk route and a mobile route. The client picks one by viewport and opens it in a new tab.
- In week 0, open every route as a plain Employee and tick "verified". The routes to verify are listed in section 4 of the brief.
- Enable `create_user_permission` on Employee (or add User Permissions) so `/desk/employee` shows only the person's own record.
- Stretch goal: show the leave balance number on Home using HRMS `get_leave_details`.

### Holidays

- Generate the Holiday List for ZA for the current and next year, add proclaimed days as rows, and point One Settings at it. Apile loads the 2026 proclaimed day (4 November) and the 2027 list.
- Acceptance test 5 then becomes checking the list against gov.za.
- Shutdown and closure days are not added here. Thithi puts them on the company holiday calendar (see below). Whether they count as leave stays an HR setting, outside the hub.

### Company holiday calendar

- One calendar appears in the hub: the company holiday calendar, owned by Thithi. Thithi connects it once in production, from the Google account that owns it, as a Google Calendar record, with pull from Google and `sync_as_public` enabled. Until then a test calendar is linked for development.
- The hub reads `Event` rows from that calendar. Admins can also add Events directly in Desk.
- Shutdown and closure days live on this calendar too, so there is no separate company dates DocType. Thithi puts "Shutdown" or "Closed" in the event title and the hub shows it as a day off. Admins can also set `one_category` on the Event in Desk.
- Repeating events show their first occurrence only. Thithi is told this; expanding repeats is not in version 1.
- Public holidays come from the Holiday List. If Thithi's calendar also contains them, the hub skips calendar events that match a Holiday List date so a holiday is not shown twice.

### Equipment (ERPNext)

The model to agree with Lindo:

- Two Stock Entry Types, both with purpose **Material Transfer**:
  - **Check Out**: Office to Site
  - **Check In**: Site to Office
- Stop using Material Issue and Material Receipt pairs for shoots, and correct the reversed "From Office To Site" type.

Once that is in place:

| View | Query |
|---|---|
| Available kit | `Bin` quantity in the Office warehouse |
| Out now | `Bin` quantity in the Site warehouse |
| Who has it | latest Check Out entry per item, via `asset_champion` |

- The Check Out button links to `/desk/stock-entry/new?stock_entry_type=Check%20Out`. Verify that v16 desk honours query string prefill. If not, add a small whitelisted method that creates a draft entry and redirects to it.
- Personally issued kit (laptops, phones) does not fit warehouse stock. Use ERPNext **Asset** with `custodian`, or serial numbers. Lindo decides; "My equipment" needs one of them.
- Moving the remaining register rows into ERPNext is data entry for Lindo, not code.

### Google Drive and ClickUp

Links only. Nothing is read from either API.

---

## 7. API

Few, coarse calls, to stay under three seconds on 4G.

| Method | Returns |
|---|---|
| `get_boot()` | Rendered into `one.html` server side, so no extra request. User and Employee (name, title, department, branch, photo from `User.user_image`), roles, settings links, HR actions, quick actions, pins, and the search index (actions, policies, resources, tools, help, the person's department toolkit) already filtered by role |
| `get_home()` | Announcements with a seen flag, next six "coming up" items (Holiday List days, company holiday calendar Events including shutdown and closure, birthdays and anniversaries), the department section (toolkit and the next date of each reminder), recently updated policies |
| `get_library()` | Policy boxes, policies, Drive resources, tools and who to ask, for People and HR, Policies and How we work. Cached by role set |
| `get_policy(name)` | One policy with its takeaways and related policies |
| `get_life(start, end)`, `get_memories()`, `get_event(name)` | Dates for a range of up to 400 days, past company events, and one company event. Any other Event is not found |
| `get_equipment(tab)` | Week 3 |
| `mark_announcements_seen(names)`, `toggle_pin(key)` | The only writes |

Rules:

- **Every method checks roles on the server.** A restricted resource URL is never sent to an employee. Vue route guards only hide navigation; the API is the real guard.
- **Caching:** content lists are cached in `frappe.cache`, keyed by role set. A `doc_events` `on_update` hook on the One DocTypes clears the cache so admin edits appear within seconds.
- **Search runs in the browser** over the boot index (a few hundred rows), like the prototype. No search endpoint in version 1.

---

## 8. Frontend

**Routes**

| Route | Page |
|---|---|
| `/one` | Home |
| `/one/hr` | People and HR |
| `/one/policies`, `/one/policies/:name` | Policies |
| `/one/life`, `/one/life/:event` | Life at Asante Solutions (list, month, memories) |
| `/one/how-we-work/:tab` | SOPs and templates, Tools we use, Who to ask, Request desk |
| `/one/equipment/:tab` | My equipment, Available kit, Full register (custodian only) |
| `/one/more` | Mobile overflow menu |

**Shell:** side rail on desktop; bottom tab bar under 860px (the prototype's breakpoints). The top bar holds search (`/` shortcut), theme toggle, notifications and the profile menu.

**Shared components:** `Avatar` (`User.user_image`, falling back to initials), `Tag`, `QuickActionTile`, `ListRow`, `Sheet` (frappe-ui Dialog), `CommandPalette`, `MonthGrid`, `DeptSection`, `PolicyBox`, `HandoffSheet` (the "this opens Frappe HR" sheet, kept only for routes still unverified).

Take the CSS tokens and layout from the prototype. Its rendering logic is template strings and should be rewritten as components rather than ported.

---

## 9. Schedule

### Week 0: before coding (mostly other people's input)

- [x] Verify every HR route as a plain Employee (Apile)
- [ ] Agree the equipment model and Stock Entry Types (Apile and Lindo)
- [ ] Policy folders on Drive organised to match the boxes (Thithi)
- [ ] Incident report template link (Thithi)
- [ ] Tool guides and what we track per tool (Thithi)
- [ ] Link a test Google calendar for development (Apile). Thithi connects the real one in production
- [x] Who to ask names: Lindokuhle Nyawo, Luthando, Wandile, Khotso (Apile). Office Champion, HR partner and Marketing still to name
- [ ] 4 November 2026 and the 2027 public holidays in the Holiday List (Apile)
- [ ] Department toolkits, quick actions and reminders (each Lead, via Thithi)
- [ ] Year end shutdown and closure dates on the company holiday calendar (Thithi)
- [ ] Friday report decision (Thithi and Muhle, asked)

### Weeks 1 to 3

| Week | Backend | Frontend | Done when |
|---|---|---|---|
| **1** | DocTypes, fixtures, roles, One Settings, `get_boot` and `get_home`, Holiday List set up, Desk workspace, seed data from the prototype (policies, resources, help, department profiles) | Scaffold, `www/one`, shell, theming, Home (greeting, announcement banner and pop up, quick actions, coming up) | Logging in lands on `/one` with a real name and photo. Thithi publishes an announcement in Desk and it pops up |
| **2** | Content APIs, reminder rule engine with tests, Google Calendar sync configured, cache invalidation | People and HR, Policies, Life (list, month, memories), How we work (four tabs), search palette, department section | Every page except Equipment works with real content. Acceptance tests 2 to 6 and 10 pass |
| **3** | Equipment API (Bin, Stock Entry, Asset), permission tests, performance pass | Equipment page, PWA manifest, 390px pass, dark mode pass, empty and error states | Acceptance tests 1, 7 to 9 and 11 pass. UAT with Thithi, then deploy |

**Main schedule risk:** if the equipment model is not agreed by the end of week 1, week 3 slips. Fallback: ship Equipment as links only (Check out, Check in, Open ERPNext, purchase list, incident template) and add the live views afterwards.

If the Friday report is confirmed, it is extra scope on top of these three weeks (section 10).

---

## 10. Open decisions

| Owner | Decision | Blocks |
|---|---|---|
| Apile and Lindo | Equipment model: Check Out and Check In as Material Transfer, `asset_champion` field, Asset or serial numbers for personally issued kit | Equipment page (week 3) |
| Thithi and Muhle | Whether the Friday report stays. Asked; awaiting an answer. If it stays, it is the one feature that stores operational records, and it needs its own estimate | Scope |
| Apile | Frappe capability list: what we use today and what we do not (requested by Muhle, 21 Oct) | Nothing in this build |
| Group | Policy folder setup: one central folder plus department copies, and how copies stay in sync | Policy content |

---

## 11. Testing

**Python (`FrappeTestCase`)**

- An Employee cannot fetch restricted resources or admin DocTypes through the API, and cannot open them in `/desk`
- Reminder dates are correct across month ends, weekends and holidays
- An announcement is returned once per user, then not again after `mark_announcement_seen`
- Audience filtering by department, branch and role
- Department profile resolves from the user's Employee record

**Playwright smoke tests**

- Log in as an employee at 390px; no horizontal scroll on any route
- HR and equipment buttons carry the expected `href`
- Admin only routes show no content for an employee

**CI:** `.github/workflows/ci.yml` already exists. Add the frontend build and the Playwright run.

### Acceptance tests (from the brief)

1. Signing in at erp.asantepower.co.za takes an employee to ASANTE ONE Home in under three seconds on 4G.
2. Home shows the person's name, role, department and photo or initials, and today's date and time in South African time.
3. Apply for leave, Request work from home and My leave balance each open the correct Frappe page in one tap, on desktop and phone.
4. An announcement published by the admin pops up once for every employee on their next visit.
5. Public holidays for the current and next year match gov.za, including Monday days in lieu and proclaimed days.
6. Each policy box opens the matching Drive folder, and each policy opens its Drive original. A policy without a document yet shows no link; the admin adds it in Desk when it is available.
7. Check out and Check in open ERPNext Stock Entry with the right type prefilled, in two taps from a phone.
8. New equipment added in ERPNext appears in Available kit without any change in ASANTE ONE.
9. An employee never sees Manage content, HR setup or restricted Drive folders, even by typing the address.
10. The admin can add an announcement, a company closure and a policy link without code.
11. Every page works on a 390 pixel wide phone without sideways scrolling.

---

## 12. Deployment runbook

1. `bench build --app asante_one` (the root `package.json` build script builds the SPA)
2. `bench --site <site> migrate` (installs DocTypes and fixtures)
3. System Settings › Default App = `asante_one`, at launch, after UAT
4. Roles: Asante One Admin for Thithi and Muhle (Administrator already sees everything through System Manager); Company Assets Custodian for Lindokuhle Nyawo. A user with a Role Profile only keeps roles that come from a profile, so add the "Asante One Admin" or "Company Assets Custodian" Role Profile (shipped as fixtures) to their role profiles; give the role directly only to users with no profile
5. Holiday List: generate ZA holidays for the current and next year, add proclaimed days, select it in One Settings
6. Google Calendar: Thithi connects the company holiday calendar with `sync_as_public`; set it in One Settings
7. Employee: confirm every employee has a User on their company email, linked to the Employee record, with `create_user_permission` set
8. Stock Entry Types: confirm Check Out and Check In exist with the agreed warehouses
9. Seed content: load or enter policies, resources, tools, help topics and department profiles
10. Smoke test as one admin and one employee on desktop and phone

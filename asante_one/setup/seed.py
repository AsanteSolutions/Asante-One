"""Starting content taken from the ASANTE ONE prototype (version 6).

Runs after install, and can be run again safely: a record that already exists is left as the
admin last saved it. Run it by hand with
	bench --site <site> execute asante_one.setup.seed.run
"""

import frappe

DRIVE = {
	"people_hr": "https://drive.google.com/drive/folders/1FR56Hbc1TltUKqSHK3n_NQA79-5CrM0a",
	"ops": "https://drive.google.com/drive/folders/1UaP48iO2ZhthxRxWmXiaDp5hCVzw_ntn",
	"admin": "https://drive.google.com/drive/folders/1JVRb6tqOSFuDXooNMu2-UpVZgV7vai1s",
	"perf": "https://drive.google.com/drive/folders/1zX-Fo8DbFM-PzQKT0TnYS4Fku8hAhXJ7",
	"sow": "https://drive.google.com/drive/folders/1-MpvVKAKwYIwlyIHPxBer2I0JhmxTCQ4",
	"journeys": "https://drive.google.com/drive/folders/1g25fu8ikA441oD7zL2_mL0ZXSISLPRgn",
	"sops": "https://drive.google.com/drive/folders/1Myit0m-P03oH6x2xa8RyemnQohZKVJjl",
	"asset_folder": "https://drive.google.com/drive/folders/1oMDG0abLCE2Fr86nwwrOkyUh4EzYs6CG",
	"training": "https://drive.google.com/drive/folders/12icpwwXalgpVcY66AA_v4NRVEfUY6LZf",
	"birthday": "https://drive.google.com/drive/folders/1zMectNX2OY6stfSM0EGlAcCM-dUzin3E",
	"initiatives": "https://drive.google.com/drive/folders/1wBc-Q3cvQigRUfqpBdiASxl_V5IvnW13",
	"important": "https://drive.google.com/drive/folders/1MzXOcAX3OuKGyJMr_1I9oS-iNa-mVUEJ",
	"weekly": "https://drive.google.com/drive/folders/1j0UV1h2TpuImjyxc1vEF1IFPAVpBrct-",
	"media": "https://drive.google.com/drive/folders/1tPuSdEiU6Vbm1FTindhlT4f0wO3JPbfK",
	"travel": "https://drive.google.com/drive/folders/17rAA62cI87v8aWnsnUSofE2QluSYjEPW",
	"ops_spend": "https://drive.google.com/drive/folders/1HGH85A94tmk5cSFNQmDlJEpwiKpHoBiu",
	"tech_errors": "https://drive.google.com/drive/folders/1VdvPgFZXjDBXoe6heeMHoYlAKLVkr0pt",
	"pluralsight": "https://drive.google.com/drive/folders/1QsDUJv-UnMz01NU7BprqOFuAOVohGzIS",
	"jhb": "https://drive.google.com/drive/folders/1KBHpAZu0BxFdE9Dls95nJBnrujsaTtSR",
	"equipment": "https://drive.google.com/drive/folders/1cToSZ1Bg0mp8MdM1ZUgJNHxoENc0bOd2",
	"sla": "https://drive.google.com/drive/folders/1O4vC5siUycq8k-YJN0IxcF7ny8BD4zq-",
	"emp_info": "https://drive.google.com/drive/folders/16rW0rRuJOvzHlzXzhaEXgcgLZAcv0Gn6",
	"applicants": "https://drive.google.com/drive/folders/1Afgyu9KvsVFyfg_6F4zunmjaQXuUGB8C",
	"wellness": "https://drive.google.com/drive/folders/1pjXqCnFhCClaGmylKRmlY2GtKeSmdzuc",
	"client_on_off": "https://drive.google.com/drive/folders/1cx2eOqaIS5bW-G0EMl_26h61IhhvDE8-",
	"assets_policy": "https://docs.google.com/document/d/16lbFsXkEwWYBUZGXsvIbuEgI08vtQAdXXSDsjR7KhEI/edit",
	"card_policy": "https://docs.google.com/document/d/1zqguu1wNuII_oYpi0tlouCi692lts_LpCHQSgchNb4Y/edit",
	"onboarding_sop": "https://docs.google.com/document/d/1_XgUfF3wvrfutGCRUWDpfcesnqY6ZTEJCSrLnUrh48g/edit",
	"clickup_sop": "https://docs.google.com/document/d/1gFx0a78Oq5k73_UWma7ZRp1nZ_RVFPO-y-tvtzLkboY/edit",
	"manifesto": "https://docs.google.com/document/d/1B_bMVuOw3ZMm08qmHbxcA7h3ox-Y7d8Kge70_rgHE7Q/edit",
	"offboarding": "https://docs.google.com/document/d/1HAzWTlpq4RIepZ30R4bjiS1pmpZRU6qOzrBR-rEtQUM/edit",
	"wms": "https://docs.google.com/document/d/1HHP5kUJvqWTXZihOyASTQv8VWtD_qC0jt9ln4xagTZs/edit",
	"ops_lead_sop": "https://docs.google.com/spreadsheets/d/1Lw_uZAZDKM034zguHr4lCmqMy46vWdNAF-Ye0S8qGfM/edit",
	"media_tracker": "https://docs.google.com/spreadsheets/d/1JIyJs298hScdXJBj2h2pL0Z0tm0YynuApnsqk02thcM/edit",
	"mm_workflow": "https://drive.google.com/file/d/10D5ME4E1nbG7szwBZEzOooUqjEBVfinG/view",
	"letterhead": "https://docs.google.com/document/d/12K_zcjXe1QS6tev8IQIHLq5U3WJJqH0levKex1vlr1U/edit",
	"brand": "https://drive.google.com/file/d/13720nwxo-ufa-G6VXss77XL5kocLXqjm/view",
	"rate_card": "https://drive.google.com/file/d/11WWh0FYfruXG2vAtdW55rKSWXrO9NA_z/view",
	"clickup_tracker": "https://docs.google.com/spreadsheets/d/11mzuxR3J6X25hjm-J4VyTYrUIRtFmfOSkDuWCpztjNY/edit",
	"recruit_manual": "https://docs.google.com/presentation/d/1TUREhVc-0_9zthwjwTM_NCUGLQxK6aYFWBSRJJKMCxc/edit",
	"bcea": "https://drive.google.com/file/d/1uHT7urxhbLqPY9x-Jv_oFhPJYYWBk29n/view",
	"ohs": "https://drive.google.com/file/d/1l2qr04C4Zhc-2aEIyFOGKW1WEiE_yDjg/view",
	"popia": "https://drive.google.com/file/d/1bXFyCpaiqzOAGoAtcJwWYGBg5rWmOipX/view",
	"ect": "https://drive.google.com/file/d/1a-gIWkNv3YH5FHnkNUAqQFFqVlLiFRfG/view",
	"equipment_process": "https://drive.google.com/file/d/1f4jLuuhSunYT2yLZ5P-mX6yaKwNW47vg/view",
	"purchase_list": "https://drive.google.com/drive/folders/1WYPSWKqkfgxFsbyIQPIWOq_Ww1NU7rG1",
}
CLICKUP = "https://app.clickup.com"
HR_ROLES = ["HR Manager", "HR User"]

# The brief's routes were opened as a plain Employee on 30 Oct 2026 and work, so they start verified.
# The rest come from the prototype and have not been checked yet.
# (key, label, module, icon, desk route, mobile route, record, verified, roles)
HR_ACTIONS = [
	(
		"leave",
		"Apply for leave",
		"Leaves",
		"leave",
		"/desk/leave-application/new",
		"/hrms/leave-applications/new",
		"Leave Application",
		1,
		None,
	),
	(
		"balance",
		"My leave balance",
		"Leaves",
		"clock",
		"/desk/query-report/Employee Leave Balance",
		"/hrms/dashboard/leaves",
		"Employee Leave Balance report",
		1,
		None,
	),
	(
		"myleave",
		"My leave requests",
		"Leaves",
		"cal",
		"/desk/leave-application",
		"/hrms/leave-applications",
		"Leave Application list",
		1,
		None,
	),
	(
		"holidays",
		"Public holidays this year",
		"Leaves",
		"flag",
		"/desk/holiday-list",
		None,
		"Holiday List",
		0,
		None,
	),
	(
		"wfh",
		"Request work from home",
		"Shift and attendance",
		"house",
		"/desk/attendance-request/new",
		"/hrms/attendance-requests/new",
		"Attendance Request (reason: Work From Home)",
		1,
		None,
	),
	(
		"checkin",
		"Check in or out",
		"Shift and attendance",
		"check",
		"/desk/employee-checkin/new",
		"/hrms/home",
		"Employee Checkin",
		1,
		None,
	),
	(
		"attendance",
		"My attendance",
		"Shift and attendance",
		"gauge",
		"/desk/attendance",
		"/hrms/dashboard/attendance",
		"Attendance list",
		1,
		None,
	),
	(
		"shift",
		"Request a shift change",
		"Shift and attendance",
		"clock",
		"/desk/shift-request/new",
		"/hrms/shift-requests/new",
		"Shift Request",
		0,
		None,
	),
	(
		"expense",
		"Claim an expense",
		"Expenses",
		"receipt",
		"/desk/expense-claim/new",
		"/hrms/expense-claims/new",
		"Expense Claim",
		1,
		None,
	),
	(
		"advance",
		"Request an advance",
		"Expenses",
		"receipt",
		"/desk/employee-advance/new",
		"/hrms/employee-advances/new",
		"Employee Advance",
		1,
		None,
	),
	(
		"myclaims",
		"My claims and status",
		"Expenses",
		"receipt",
		"/desk/expense-claim",
		"/hrms/expense-claims",
		"Expense Claim list",
		0,
		None,
	),
	("goals", "My goals", "Performance", "gauge", "/desk/goal", None, "Goal", 1, None),
	("appraisal", "My appraisal", "Performance", "gauge", "/desk/appraisal", None, "Appraisal", 1, None),
	(
		"feedback",
		"Give feedback",
		"Performance",
		"chat",
		"/desk/employee-performance-feedback/new",
		None,
		"Employee Performance Feedback",
		0,
		None,
	),
	("openings", "Open roles", "Recruitment", "recruit", "/desk/job-opening", None, "Job Opening", 1, None),
	(
		"referral",
		"Refer someone",
		"Recruitment",
		"recruit",
		"/desk/employee-referral/new",
		None,
		"Employee Referral",
		1,
		None,
	),
	(
		"interviews",
		"My interviews to score",
		"Recruitment",
		"recruit",
		"/desk/interview",
		None,
		"Interview (panel members only)",
		0,
		None,
	),
	(
		"onboard",
		"My onboarding steps",
		"Tenure",
		"tenure",
		"/desk/employee-onboarding",
		None,
		"Employee Onboarding",
		0,
		None,
	),
	(
		"grievance",
		"Raise a confidential concern",
		"Tenure",
		"shield",
		"/desk/employee-grievance/new",
		None,
		"Employee Grievance",
		1,
		None,
	),
	(
		"profile",
		"My employee profile",
		"Tenure",
		"user",
		"/desk/employee",
		"/hrms/profile",
		"Employee (own record only)",
		1,
		None,
	),
	(
		"payslip",
		"My payslips",
		"Tax and benefits",
		"tax",
		"/desk/salary-slip",
		"/hrms/dashboard/salary-slips",
		"Salary Slip (only if payroll runs in Frappe)",
		1,
		None,
	),
	(
		"benefit",
		"Claim a benefit",
		"Tax and benefits",
		"tax",
		"/desk/employee-benefit-claim/new",
		None,
		"Employee Benefit Claim",
		0,
		None,
	),
	(
		"hrsettings",
		"HR settings, leave types, holiday lists",
		"HR setup",
		"setup",
		"/desk/hr-settings",
		None,
		"HR Settings (People and Culture only)",
		0,
		HR_ROLES,
	),
]

# The same quick actions for everyone. The brief's sixth, Incident report, is added once the template link exists.
QUICK_ACTIONS = [
	{
		"label": "Apply for leave",
		"subtitle": "Frappe HR",
		"icon": "leave",
		"action_type": "HR Action",
		"hr_action": "leave",
	},
	{
		"label": "Request work from home",
		"subtitle": "Frappe HR",
		"icon": "house",
		"action_type": "HR Action",
		"hr_action": "wfh",
	},
	{
		"label": "My leave balance",
		"subtitle": "Frappe HR",
		"icon": "clock",
		"action_type": "HR Action",
		"hr_action": "balance",
	},
	{
		"label": "Find a policy",
		"subtitle": "Policies",
		"icon": "book",
		"action_type": "Page",
		"page": "/policies",
	},
	{"label": "My tasks", "subtitle": "Opens ClickUp", "icon": "check", "action_type": "URL", "url": CLICKUP},
]

# (title, icon, Drive folder URL, Drive folder name)
POLICY_BOXES = [
	("People and HR", "people", DRIVE["people_hr"], "AS | People & HR"),
	("Finance", "receipt", None, None),
	("Operations", "map", DRIVE["asset_folder"], "Current Administration policy folder"),
	("How we work", "check", DRIVE["sops"], "Standard Operating Procedures"),
	("Culture", "heart", None, None),
	("Compliance", "shield", None, None),
	("Legislation", "book", DRIVE["asset_folder"], "Current Administration policy folder"),
]

# key, title, box, owner, status, updated on, url, summary, takeaways, related keys.
# The key only links related policies here; it is not stored.
POLICIES = [
	(
		"assets",
		"Assets Policy",
		"Operations",
		"Operations Lead",
		"Status to verify",
		"2026-03-06",
		DRIVE["assets_policy"],
		"How company equipment is issued, cared for, tracked and returned.",
		[
			"Every device you receive is logged against your name by the Company Assets Custodian.",
			"Report loss or damage the same day.",
			"Equipment is returned on your last working day.",
		],
		["offboard"],
	),
	(
		"card",
		"Company Card and Offsite Spend Policy",
		"Finance",
		"Finance Lead",
		"Draft",
		"2026-10-14",
		DRIVE["card_policy"],
		"Rules for using the company card and spending money away from the office.",
		[
			"Draft v2: open for comment, not yet in force.",
			"Once approved, every spend is claimed in Frappe HR under Expenses with a receipt.",
		],
		[],
	),
	(
		"onboarding",
		"Onboarding SOP",
		"People and HR",
		"People and Culture",
		"Status to verify",
		"2026-06-25",
		DRIVE["onboarding_sop"],
		"What happens in a new team member's first days and weeks.",
		[
			"Every new joiner gets accounts, a buddy and a first week plan.",
			"The Recruitment, Onboarding and Offboarding Manual is the companion document.",
		],
		["recruitman"],
	),
	(
		"offboard",
		"Offboarding Checklist",
		"People and HR",
		"People and Culture",
		"Status to verify",
		"2026-03-25",
		DRIVE["offboarding"],
		"Steps to close out a role cleanly: handover, assets, access and exit.",
		[
			"Access to Drive, ClickUp and AsantePower is removed on the last day.",
			"Assets are checked against the asset register.",
		],
		["assets"],
	),
	(
		"clickup",
		"ClickUp SOP",
		"How we work",
		"Operations Lead",
		"Status to verify",
		"2026-07-16",
		DRIVE["clickup_sop"],
		"How every person logs, updates and closes their own work in ClickUp.",
		["Log all of your own work, do not wait for someone to create tasks for you."],
		["wms"],
	),
	(
		"manifesto",
		"How We Work Manifesto",
		"Culture",
		"Managing Director",
		"Status to verify",
		"2026-01-08",
		DRIVE["manifesto"],
		"The way Asante Solutions works, decides and treats clients and each other.",
		['The foundation for "The Asante Way" customer experience standard being defined now.'],
		[],
	),
	(
		"wms",
		"Work Management System Reset",
		"How we work",
		"Managing Director",
		"Status to verify",
		"2026-07-01",
		DRIVE["wms"],
		"The reset of how work is planned, tracked and reported across the company.",
		["Read with the ClickUp SOP."],
		["clickup"],
	),
	(
		"recruitman",
		"Recruitment, Onboarding and Offboarding Manual",
		"People and HR",
		"People and Culture",
		"Status to verify",
		"2026-07-29",
		DRIVE["recruit_manual"],
		"The full people lifecycle in one manual. Three copies exist in Drive: this is the newest.",
		["Archive the two older copies so search only finds one."],
		["onboarding"],
	),
	(
		"recruitold",
		"Recruitment and Onboarding Framework (older copies)",
		"People and HR",
		"People and Culture",
		"Archived",
		None,
		None,
		"Superseded by the Recruitment, Onboarding and Offboarding Manual. Kept for history only.",
		["Do not use. Open the current manual instead."],
		["recruitman"],
	),
	(
		"leavep",
		"Leave Policy",
		"People and HR",
		"People and Culture",
		"Missing",
		None,
		None,
		"Not found in Drive. Needed before the Apply for leave button means anything.",
		[],
		[],
	),
	(
		"wfhp",
		"Work From Home Policy",
		"People and HR",
		"People and Culture",
		"Missing",
		None,
		None,
		"Not found in Drive. Defines who may work from home, how often, and who approves.",
		[],
		[],
	),
	(
		"handbook",
		"Employee Handbook",
		"People and HR",
		"People and Culture",
		"Missing",
		None,
		None,
		"Not found in Drive. The single starting document for every new joiner.",
		[],
		[],
	),
	(
		"conduct",
		"Code of Conduct and Disciplinary Procedure",
		"People and HR",
		"People and Culture with HR partner",
		"Missing",
		None,
		None,
		"Not found in Drive. Required for fair process under South African labour law.",
		[],
		[],
	),
	(
		"privacy",
		"Employee Privacy Notice (POPIA)",
		"Compliance",
		"People and Culture",
		"Missing",
		None,
		None,
		"Not found in Drive. Explains how employee information is used.",
		[],
		[],
	),
	(
		"itpolicy",
		"IT, Devices and Acceptable Use Policy",
		"Operations",
		"Technical Lead",
		"Missing",
		None,
		None,
		"Not found in Drive. Covers passwords, client data and AsantePower access.",
		[],
		[],
	),
	(
		"ohsact",
		"Occupational Health and Safety Act 85 of 1993",
		"Legislation",
		"Operations Lead",
		"Legislation",
		None,
		DRIVE["ohs"],
		"Reference copy of the Act. Not a company policy.",
		[],
		[],
	),
	(
		"bceaact",
		"Basic Conditions of Employment Act 75 of 1997",
		"Legislation",
		"People and Culture",
		"Legislation",
		None,
		DRIVE["bcea"],
		"Reference copy of the Act. Not a company policy.",
		[],
		[],
	),
	(
		"popiaact",
		"Protection of Personal Information Act",
		"Legislation",
		"People and Culture",
		"Legislation",
		None,
		DRIVE["popia"],
		"Reference copy of the Act. Not a company policy.",
		[],
		[],
	),
	(
		"ectact",
		"Electronic Communications and Transactions Act 25 of 2002",
		"Legislation",
		"Technical Lead",
		"Legislation",
		None,
		DRIVE["ect"],
		"Reference copy of the Act. Not a company policy.",
		[],
		[],
	),
]

PEOPLE_AND_CULTURE = ["Asante One Admin", "HR Manager"]
LEADS = ["Asante One Admin", "HR Manager"]
# title, url, category, description, owner, who can open, restricted roles.
# The prototype marked these folders restricted; until real roles exist they are limited to People and Culture.
RESOURCES = [
	(
		"People and HR",
		DRIVE["people_hr"],
		"People and HR",
		"Scopes of work, performance workbooks, consultation guides",
		"Thithi",
		"People and Culture, Leads",
		PEOPLE_AND_CULTURE,
	),
	(
		"Performance Management",
		DRIVE["perf"],
		"People and HR",
		"Workbooks, quarterly reviews, monthly self check ins by role",
		"Thithi",
		"Each person sees their own role files",
		None,
	),
	(
		"Scope of Work Documents",
		DRIVE["sow"],
		"People and HR",
		"Every role's scope of work",
		"Thithi",
		"Everyone, read only",
		None,
	),
	(
		"Role Journey Diagrams",
		DRIVE["journeys"],
		"People and HR",
		"Visual growth path for each role",
		"Thithi",
		"Everyone, read only",
		None,
	),
	(
		"Birthday Framework",
		DRIVE["birthday"],
		"Culture",
		"How birthdays are celebrated and budgeted",
		"Thithi",
		"Everyone, read only",
		None,
	),
	(
		"People Wellness Brand Assets",
		DRIVE["wellness"],
		"Culture",
		"Bloom Briefs design assets",
		"Thithi",
		"People and Culture",
		None,
	),
	(
		"New Applicants",
		DRIVE["applicants"],
		"People and HR",
		"Applicant files for open roles",
		"Thithi",
		"Hiring panel only",
		PEOPLE_AND_CULTURE,
	),
	(
		"Employee Information",
		DRIVE["emp_info"],
		"People and HR",
		"Personal records. Never linked for general access",
		"Thithi",
		"People and Culture, MD",
		PEOPLE_AND_CULTURE,
	),
	(
		"Operations (OperationsX)",
		DRIVE["ops"],
		"Operations",
		"The overall Operations Drive",
		"Operations Lead",
		"Everyone, read only",
		None,
	),
	(
		"Administration",
		DRIVE["admin"],
		"Operations",
		"Admin, SOPs, initiatives, company documents",
		"Operations Lead",
		"Leads",
		None,
	),
	(
		"Standard Operating Procedures",
		DRIVE["sops"],
		"Operations",
		"All company SOPs in one folder",
		"Operations Lead",
		"Everyone, read only",
		None,
	),
	(
		"Operations Lead Role SOP",
		DRIVE["ops_lead_sop"],
		"Operations",
		"Day to day operations playbook",
		"Operations Lead",
		"Leads",
		None,
	),
	(
		"Client Onboarding and Offboarding",
		DRIVE["client_on_off"],
		"Operations",
		"How clients are welcomed and closed out",
		"Client Success Lead",
		"Everyone, read only",
		None,
	),
	(
		"Service Level Agreements",
		DRIVE["sla"],
		"Operations",
		"Signed client SLAs",
		"Client Success Lead",
		"Leads",
		LEADS,
	),
	(
		"Multimedia Workflow: Story to Impact",
		DRIVE["mm_workflow"],
		"Operations",
		"How a shoot moves from brief to delivery",
		"Media Production Lead",
		"Everyone, read only",
		None,
	),
	(
		"Media Production Tracker",
		DRIVE["media_tracker"],
		"Operations",
		"Shoots and delivery status",
		"Media Production Lead",
		"Media team",
		None,
	),
	(
		"Media Calendars",
		DRIVE["media"],
		"Operations",
		"Content calendars",
		"Marketing Lead",
		"Marketing and media",
		None,
	),
	(
		"Website and CRM: Technical Errors",
		DRIVE["tech_errors"],
		"Operations",
		"Where CRM and website faults are logged today",
		"Technical Lead",
		"Everyone can add",
		None,
	),
	(
		"Travel (Uber and Bolt)",
		DRIVE["travel"],
		"Operations",
		"Trip receipts and travel records",
		"Operations Lead",
		"Everyone can add",
		None,
	),
	(
		"Operations Expenditure",
		DRIVE["ops_spend"],
		"Operations",
		"Operational spend records",
		"Finance Lead",
		"Finance, MD",
		LEADS,
	),
	(
		"Equipment",
		DRIVE["equipment"],
		"Operations",
		"Equipment records",
		"Company Assets Custodian",
		"Operations",
		None,
	),
	(
		"JHB Office",
		DRIVE["jhb"],
		"Operations",
		"Johannesburg office set up and admin",
		"Thithi",
		"JHB team",
		None,
	),
	(
		"Weekly Reports",
		DRIVE["weekly"],
		"Operations",
		"Old home of reports. Last updated Jan 2026",
		"Thithi",
		"Leads",
		None,
	),
	(
		"Initiatives (funding, tenders, awards)",
		DRIVE["initiatives"],
		"Growth",
		"Every bid and application folder",
		"Thithi",
		"Growth team, Leads",
		None,
	),
	(
		"Company documents for tenders",
		DRIVE["important"],
		"Growth",
		"BBBEE certificate, affidavit, AFS, letterheads",
		"Thithi",
		"Growth team, MD",
		LEADS,
	),
	(
		"Rate Card (2025)",
		DRIVE["rate_card"],
		"Growth",
		"Internal pricing for proposals",
		"Thithi",
		"Growth and sales",
		None,
	),
	(
		"Purple Letterhead",
		DRIVE["letterhead"],
		"Templates",
		"Official letterhead template",
		"Marketing Lead",
		"Everyone, read only",
		None,
	),
	(
		"Brand Assets",
		DRIVE["brand"],
		"Templates",
		"Logos, colours and brand files",
		"Marketing Lead",
		"Everyone, read only",
		None,
	),
	(
		"Staff Training",
		DRIVE["training"],
		"Learning",
		"Internal training material",
		"Thithi",
		"Everyone, read only",
		None,
	),
	(
		"Pluralsight: Tech and Engineering Skills",
		DRIVE["pluralsight"],
		"Learning",
		"Technical learning paths",
		"Technical Lead",
		"Tech team",
		None,
	),
	(
		"ClickUp Usage Tracker",
		DRIVE["clickup_tracker"],
		"People and HR",
		"Adoption assessment used in check ins",
		"Thithi",
		"Thithi, MD",
		PEOPLE_AND_CULTURE,
	),
]

# tool, what it is for, who uses it, url, guide url, what we track
TOOLS = [
	(
		"ClickUp",
		"Work management: every task and project",
		"Everyone",
		CLICKUP,
		DRIVE["clickup_sop"],
		"Tasks done on time, overdue tasks, workload per person",
	),
	(
		"AsantePower: Frappe HR",
		"People management: leave, attendance, claims, payslips",
		"Everyone",
		"/desk",
		None,
		"Leave taken, claims turnaround, attendance",
	),
	(
		"AsantePower: ERPNext",
		"Equipment: register, check out and check in, stock ledger",
		"Media Production, Company Assets Custodian",
		"/desk",
		DRIVE["equipment_process"],
		"Items checked out, items not yet checked back in",
	),
	(
		"AsantePower CRM",
		"Go to market: leads, pipeline, client follow ups",
		"Growth and Partnerships, Client Success",
		"https://asantepower.co.za",
		None,
		"Pipeline value by stage, conversion, follow ups due",
	),
	(
		"Google Drive",
		"Storage: all company documents and the policy library",
		"Everyone",
		"https://drive.google.com",
		DRIVE["wms"],
		"Files in the right folder, links that still work",
	),
	(
		"Google Workspace email and calendar",
		"Communication and meetings",
		"Everyone",
		"https://mail.google.com",
		None,
		"Response times on client email",
	),
	(
		"Metricool",
		"Social scheduling, analytics and client social reports",
		"Marketing",
		"https://app.metricool.com",
		None,
		"Reach, engagement, posts published against plan",
	),
	(
		"Xero",
		"Accounting: invoices, bills, bank reconciliation",
		"Finance",
		"https://go.xero.com",
		None,
		"Cash position, debtor days, month end closed on time",
	),
	(
		"Canva",
		"Design and social templates",
		"Marketing, Media Production (confirm)",
		"https://www.canva.com",
		None,
		None,
	),
	("Figma", "Product and interface design", "Technology (confirm)", "https://www.figma.com", None, None),
]

# group, ask about, role, person (matched to an Employee by full name)
HELP_TOPICS = [
	(
		"People and HR",
		"Leave, work from home, contracts, check ins, onboarding",
		"Growth and People Lead",
		"Thithi Masuku",
	),
	("People and HR", "A confidential concern about work", "HR partner", None),
	(
		"Approvals and direction",
		"Approvals on your Friday report, company direction",
		"Managing Director",
		"Muhle Ndwalane",
	),
	(
		"Equipment and the office",
		"Equipment register, check out and check in, equipment purchases",
		"Company Assets Custodian",
		"Lindokuhle Nyawo",
	),
	("Equipment and the office", "Equipment on a shoot or on site", "Asset Champion for that shoot", None),
	(
		"Equipment and the office",
		"Cleaning, kitchen, supplies, WiFi or power, the space",
		"Office Champion",
		None,
	),
	(
		"Systems and tech",
		"AsantePower CRM, websites, logins, ASANTE ONE",
		"Technical Lead",
		"Luthando Mohlakoana",
	),
	("Money", "Claims, card spend, invoices, payslips", "Finance Lead", "Wandile Nontokozo Mashinini"),
	(
		"Clients and delivery",
		"Shoot briefs and client deliverables",
		"Client Success Lead",
		"Khotso Falang Ntaba",
	),
	("Clients and delivery", "Brand files, letterheads, social media", "Marketing", None),
]

# Topics listed on the Request desk: the request's name and where it is made
REQUESTS = {
	"Equipment register, check out and check in, equipment purchases": (
		"Equipment request",
		DRIVE["purchase_list"],
	),
	"AsantePower CRM, websites, logins, ASANTE ONE": ("CRM or website issue", DRIVE["tech_errors"]),
	"Brand files, letterheads, social media": ("Brand asset", DRIVE["brand"]),
}


def tool(label, subtitle, url, icon, status="Link"):
	return {"label": label, "subtitle": subtitle, "url": url, "icon": icon, "status": status}


def weekly(title, description, weekday, kind="Company rhythm"):
	return {"title": title, "description": description, "kind": kind, "rule": "Weekly", "weekday": weekday}


def last_business_day(title, description, kind="Company rhythm"):
	return {"title": title, "description": description, "kind": kind, "rule": "Last business day of month"}


def monthly(title, description, day, kind="SARS rule"):
	return {"title": title, "description": description, "kind": kind, "rule": "Monthly on day", "day": day}


def yearly(title, description, day, month, kind="SARS rule"):
	return {
		"title": title,
		"description": description,
		"kind": kind,
		"rule": "Yearly on date",
		"day": day,
		"month": month,
	}


def page(label, subtitle, icon, to):
	return {"label": label, "subtitle": subtitle, "icon": icon, "action_type": "Page", "page": to}


def link(label, subtitle, icon, url):
	return {"label": label, "subtitle": subtitle, "icon": icon, "action_type": "URL", "url": url}


def hr(label, subtitle, icon, key):
	return {"label": label, "subtitle": subtitle, "icon": icon, "action_type": "HR Action", "hr_action": key}


# Matched to a Department by its department name (without the company suffix).
# Client Success is part of Operations, so its tools and reminders are in the Operations profile.
# Service Level Agreements stays out of it: it is restricted to Leads and department tools are not.
DEPARTMENTS = {
	("Human Resources",): {
		"display_name": "Growth and People",
		"quick_actions": [
			page("People and HR", "Frappe HR view", "people", "/hr"),
			page("How we work", "SOPs, tools, who to ask", "map", "/how-we-work"),
		],
		"tools": [
			tool("Frappe HR desk", "Leave approvals, employee records", "/desk", "people", "Route to verify"),
			tool("ClickUp", "Operations and Sales lists", CLICKUP, "check"),
			tool("ClickUp Usage Tracker", "Adoption check ins", DRIVE["clickup_tracker"], "gauge"),
			tool("Performance Management", "Workbooks and reviews", DRIVE["perf"], "folder"),
			tool("Initiatives (funding and tenders)", "Every bid folder", DRIVE["initiatives"], "folder"),
			tool("Read AI", "Meeting notes", "https://app.read.ai", "chat", "Confirm team uses it"),
		],
		"reminders": [
			weekly("Monday FA Meeting", "11:00 to 13:00, 10 minutes per person", "Monday"),
			last_business_day("Monthly people check ins", "Last working day of the month"),
		],
	},
	("Media Production",): {
		"quick_actions": [
			page("Available kit", "Shoot kit in the office", "camera", "/equipment/kit"),
			page("My equipment", "Kit you have out", "box", "/equipment"),
		],
		"tools": [
			tool("ERPNext: equipment", "Check outs and check ins", "/desk/stock-entry", "box"),
			tool(
				"Equipment process",
				"Check out, checks, labels, Asset Champion",
				DRIVE["equipment_process"],
				"book",
			),
			tool("Media Production Tracker", "Shoots and delivery status", DRIVE["media_tracker"], "camera"),
			tool("Multimedia Workflow", "Story to impact", DRIVE["mm_workflow"], "map"),
			tool("Media Calendars", "Content and shoot calendars", DRIVE["media"], "cal"),
			tool(
				"Canva",
				"Quick edits and social cuts",
				"https://www.canva.com",
				"star",
				"Confirm team uses it",
			),
			tool("Brand Assets", "Logos and brand files", DRIVE["brand"], "star"),
		],
		"reminders": [
			weekly("Offload and back up shoot cards", "Before cards go back into the kit", "Friday")
		],
	},
	("Digital Marketing", "Marketing"): {
		"display_name": "Marketing",
		"quick_actions": [
			link("Open Metricool", "Social scheduling", "spark", "https://app.metricool.com"),
			link("Content calendar", "Google Drive", "cal", DRIVE["media"]),
		],
		"tools": [
			tool("Metricool", "Scheduling, analytics, social reports", "https://app.metricool.com", "spark"),
			tool(
				"Canva",
				"Design and social templates",
				"https://www.canva.com",
				"star",
				"Confirm team uses it",
			),
			tool(
				"Porter Metrics",
				"Client reporting dashboards",
				"https://portermetrics.com",
				"gauge",
				"Confirm team uses it",
			),
			tool("Media Calendars", "Content calendar", DRIVE["media"], "cal"),
			tool("Brand Assets", "Logos and brand files", DRIVE["brand"], "star"),
			tool("Purple Letterhead", "Official template", DRIVE["letterhead"], "report"),
		],
		"reminders": [
			last_business_day(
				"Next month's content calendar locked",
				"Plan in Media Calendars, schedule in Metricool",
				"Suggested",
			),
		],
	},
	("Technology",): {
		"quick_actions": [
			link("Log a CRM or website fault", "Technical Errors log", "alert", DRIVE["tech_errors"]),
			link("AsantePower desk", "erp.asantepower.co.za", "grid", "/desk"),
		],
		"tools": [
			tool("AsantePower desk", "CRM, HR and platform admin", "/desk", "grid"),
			tool("AsantePower platform", "Client facing CRM product", "https://asantepower.co.za", "spark"),
			tool("Website and CRM: Technical Errors", "Fault log", DRIVE["tech_errors"], "alert"),
			tool(
				"Figma",
				"Product and interface design",
				"https://www.figma.com",
				"star",
				"Confirm team uses it",
			),
			tool("Pluralsight", "Tech learning paths", DRIVE["pluralsight"], "book"),
			tool("ClickUp", "Tech and client delivery lists", CLICKUP, "check"),
		],
		"reminders": [
			weekly("Tech team meeting", "Every Thursday", "Thursday"),
			weekly(
				"Review open CRM and website faults",
				"Weekly, from the Technical Errors log",
				"Monday",
				"Suggested",
			),
			last_business_day(
				"Client subscription and renewal check", "AsantePower clients due for renewal", "Suggested"
			),
		],
	},
	("Accounts",): {
		"display_name": "Finance",
		"quick_actions": [
			link("Open Xero", "Accounting", "tax", "https://go.xero.com"),
			hr("Claims to approve", "Frappe HR", "receipt", "myclaims"),
		],
		"tools": [
			tool("Xero", "Invoices, bills, bank reconciliation", "https://go.xero.com", "tax"),
			tool("SARS eFiling", "EMP201, VAT201, EMP501", "https://www.sarsefiling.co.za", "shield"),
			tool(
				"Frappe HR Expenses", "Claims to approve", "/desk/expense-claim", "receipt", "Route to verify"
			),
			tool("Company Card and Offsite Spend Policy", "Draft v2", DRIVE["card_policy"], "book"),
			tool("Operations Expenditure", "Spend records", DRIVE["ops_spend"], "folder"),
			tool("Rate Card (2025)", "Pricing for quotes", DRIVE["rate_card"], "report"),
		],
		"reminders": [
			monthly(
				"EMP201 (PAYE, UIF, SDL)", "SARS: submit and pay by the 7th, or the working day before", 7
			),
			yearly("EMP501 interim reconciliation", "SARS window closes 31 October", 31, "October"),
			yearly("EMP501 annual reconciliation", "SARS window closes 31 May", 31, "May"),
			last_business_day(
				"Month end close in Xero", "Reconcile bank feeds, lock the period", "Suggested"
			),
			monthly("Payroll run", "Date to confirm with Finance", 25, "Confirm"),
		],
	},
	("Sales",): {
		"display_name": "Growth and Partnerships",
		"quick_actions": [
			link("Open the CRM", "AsantePower", "grid", "https://asantepower.co.za"),
			link("Rate card", "Pricing", "report", DRIVE["rate_card"]),
		],
		"tools": [
			tool("AsantePower CRM", "Pipeline, leads and follow ups", "https://asantepower.co.za", "grid"),
			tool("Rate Card (2025)", "Pricing for proposals", DRIVE["rate_card"], "report"),
			tool("Initiatives (funding and tenders)", "Bid folders", DRIVE["initiatives"], "folder"),
			tool("Brand Assets", "Company profile and logos", DRIVE["brand"], "star"),
			tool("ClickUp", "Sales list", CLICKUP, "check"),
		],
		"reminders": [
			weekly("Growth department session", "Pipeline review", "Wednesday"),
			weekly(
				"Follow up proposals in negotiation",
				"The longest stage in our pipeline",
				"Tuesday",
				"Suggested",
			),
		],
	},
	("Operations",): {
		"quick_actions": [
			page("Equipment", "Kit and who has it", "camera", "/equipment/out"),
			link("Purchase list", "Equipment requests", "receipt", DRIVE["purchase_list"]),
		],
		"tools": [
			tool(
				"ERPNext: equipment register", "Items, check outs, stock ledger", "/desk/stock-entry", "box"
			),
			tool("Equipment purchase list", "Requests and purchases", DRIVE["purchase_list"], "receipt"),
			tool(
				"Equipment process",
				"Lindo's check out and accountability process",
				DRIVE["equipment_process"],
				"book",
			),
			tool("Assets Policy", "Rules for company equipment", DRIVE["assets_policy"], "book"),
			tool("Travel (Uber and Bolt)", "Trip receipts", DRIVE["travel"], "map"),
			tool(
				"Client Onboarding and Offboarding",
				"How clients are welcomed and closed out",
				DRIVE["client_on_off"],
				"folder",
			),
			tool("Media Production Tracker", "Status of client shoots", DRIVE["media_tracker"], "camera"),
			tool("ClickUp", "Client Success list", CLICKUP, "check"),
			tool("Read AI", "Client meeting notes", "https://app.read.ai", "chat", "Confirm team uses it"),
		],
		"reminders": [
			last_business_day("Monthly equipment count in ERPNext", "Condition check on shared kit"),
			weekly("Check all shoot kit is checked back in", "Before the weekend", "Friday", "Suggested"),
			weekly(
				"Weekly client check ins", "Agendas from each client's ClickUp list", "Monday", "Suggested"
			),
			last_business_day(
				"Monthly client value reports", "Progress and value report per retainer client", "Suggested"
			),
		],
	},
}


def run():
	seed_hr_actions()
	seed_settings()
	seed_policies()
	seed_resources()
	seed_tools()
	seed_help_topics()
	seed_department_profiles()
	frappe.db.commit()


def seed_hr_actions():
	for seq, (key, label, module, icon, desk, mobile, record, verified, roles) in enumerate(HR_ACTIONS, 1):
		if frappe.db.exists("One HR Action", key):
			continue
		doc = frappe.get_doc(
			{
				"doctype": "One HR Action",
				"action_key": key,
				"label": label,
				"module": module,
				"icon": icon,
				"desk_route": desk,
				"mobile_route": mobile,
				"record": record,
				"verified": verified,
				"sequence": seq,
			}
		)
		for role in roles or []:
			if frappe.db.exists("Role", role):
				doc.append("roles", {"role": role})
		doc.insert(ignore_permissions=True)


def seed_settings():
	settings = frappe.get_single("One Settings")
	if settings.quick_actions:
		return
	for row in QUICK_ACTIONS:
		settings.append("quick_actions", row)
	settings.clickup_url = settings.clickup_url or CLICKUP
	settings.operations_drive_url = settings.operations_drive_url or DRIVE["ops"]
	settings.purchase_list_url = settings.purchase_list_url or DRIVE["purchase_list"]
	settings.equipment_process_url = settings.equipment_process_url or DRIVE["equipment_process"]
	if not settings.holiday_list:
		company = frappe.defaults.get_global_default("company")
		settings.holiday_list = company and frappe.db.get_value("Company", company, "default_holiday_list")
	settings.save(ignore_permissions=True)


def seed_policies():
	for seq, (title, icon, url, folder) in enumerate(POLICY_BOXES, 1):
		if not frappe.db.exists("One Policy Box", title):
			frappe.get_doc(
				{
					"doctype": "One Policy Box",
					"title": title,
					"icon": icon,
					"sequence": seq,
					"drive_folder_url": url,
					"drive_folder_name": folder,
				}
			).insert(ignore_permissions=True)

	names = {}
	for key, title, box, owner, status, updated, url, summary, takeaways, _related in POLICIES:
		names[key] = frappe.db.get_value("One Policy", {"title": title})
		if names[key]:
			continue
		doc = frappe.get_doc(
			{
				"doctype": "One Policy",
				"title": title,
				"box": box,
				"policy_owner": owner,
				"status": status,
				"updated_on": updated,
				"drive_url": url,
				"summary": summary,
				"takeaways": [{"takeaway": t} for t in takeaways],
			}
		).insert(ignore_permissions=True)
		names[key] = doc.name

	for key, *_rest, related in POLICIES:
		doc = frappe.get_doc("One Policy", names[key])
		if doc.related or not related:
			continue
		for other in related:
			doc.append("related", {"policy": names[other]})
		doc.save(ignore_permissions=True)


def seed_resources():
	for title, url, category, description, owner, who, roles in RESOURCES:
		if frappe.db.exists("One Resource", {"title": title}):
			continue
		doc = frappe.get_doc(
			{
				"doctype": "One Resource",
				"title": title,
				"url": url,
				"category": category,
				"description": description,
				"content_owner": owner,
				"who_can_open": who,
			}
		)
		for role in roles or []:
			if frappe.db.exists("Role", role):
				doc.append("restricted_roles", {"role": role})
		doc.insert(ignore_permissions=True)


def seed_tools():
	for seq, (name, purpose, used_by, url, guide, tracked) in enumerate(TOOLS, 1):
		if frappe.db.exists("One Tool", name):
			continue
		frappe.get_doc(
			{
				"doctype": "One Tool",
				"tool_name": name,
				"purpose": purpose,
				"used_by": used_by,
				"url": url,
				"guide_url": guide,
				"tracked_measures": tracked,
				"sequence": seq,
			}
		).insert(ignore_permissions=True)


def seed_help_topics():
	for seq, (group, question, role, person) in enumerate(HELP_TOPICS, 1):
		if frappe.db.exists("One Help Topic", {"question": question}):
			continue
		employee = person and frappe.db.get_value("Employee", {"employee_name": person, "status": "Active"})
		request_label, request_url = REQUESTS.get(question, (None, None))
		frappe.get_doc(
			{
				"doctype": "One Help Topic",
				"help_group": group,
				"question": question,
				"role": role,
				"person": employee,
				"request_label": request_label,
				"request_url": request_url,
				"sequence": seq,
			}
		).insert(ignore_permissions=True)


def seed_department_profiles():
	for department_names, profile in DEPARTMENTS.items():
		department = next(
			filter(
				None, (frappe.db.get_value("Department", {"department_name": n}) for n in department_names)
			),
			None,
		)
		if not department or frappe.db.exists("One Department Profile", department):
			continue
		frappe.get_doc(
			{
				"doctype": "One Department Profile",
				"department": department,
				"display_name": profile.get("display_name"),
				"quick_actions": profile["quick_actions"],
				"tools": profile["tools"],
				"reminders": profile["reminders"],
			}
		).insert(ignore_permissions=True)

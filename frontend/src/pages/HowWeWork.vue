<template>
	<div class="mb-[18px] mt-1 flex flex-col gap-4 nav:flex-row nav:items-end nav:justify-between">
		<div>
			<h1 class="page-title">How we work</h1>
			<p class="page-lede">Start here if you are new. Our SOPs and templates, the tools we use, who to ask for what, and where requests go.</p>
		</div>
		<div class="flex flex-wrap gap-2">
			<a v-if="boot.links.operations_drive" :href="boot.links.operations_drive" target="_blank" rel="noopener" class="btn">
				<Icon name="folder" class="h-4 w-4" /> Operations Drive
			</a>
			<a v-if="boot.links.clickup" :href="boot.links.clickup" target="_blank" rel="noopener" class="btn">
				<Icon name="ext" class="h-4 w-4" /> ClickUp
			</a>
		</div>
	</div>

	<nav class="-mx-4 mb-6 flex gap-0.5 overflow-x-auto border-b border-line px-4 nav:mx-0 nav:px-0" aria-label="How we work">
		<RouterLink
			v-for="t in TABS"
			:key="t.key"
			:to="`/how-we-work/${t.key}`"
			class="-mb-px whitespace-nowrap border-b-2 px-3.5 py-2.5 text-sm font-semibold no-underline"
			:class="tab === t.key ? 'border-accent-bg text-ink' : 'border-transparent text-grey hover:text-ink'"
			:aria-current="tab === t.key ? 'page' : undefined"
		>
			{{ t.label }}
		</RouterLink>
	</nav>

	<p v-if="library.error" class="hint">This page could not load. Refresh the page to try again.</p>
	<Skeleton v-else-if="!library.data" :rows="6" />

	<!-- SOPs and templates -->
	<template v-else-if="tab === 'sops'">
		<input v-model="query" class="input mb-4 nav:max-w-[320px]" placeholder="Filter SOPs, folders and templates" aria-label="Filter SOPs, folders and templates" />
		<div class="grid grid-cols-1 items-start gap-4 nav:grid-cols-2">
			<section v-if="sops.length" class="panel">
				<h2 class="text-lg">How we work</h2>
				<div class="mt-1.5 flex flex-col">
					<LinkRow v-for="p in sops" :key="p.name" :to="`/policies/${p.name}`" icon="book" :title="p.title" :subtitle="p.summary" />
				</div>
			</section>
			<section v-for="group in folders" :key="group.category" class="panel">
				<h2 class="text-lg">{{ group.category }}</h2>
				<div class="mt-1.5 flex flex-col">
					<LinkRow v-for="r in group.items" :key="r.name" :href="r.url" icon="folder" :title="r.title" :subtitle="[r.description, r.content_owner && `Owner: ${r.content_owner}`].filter(Boolean).join(' · ')">
						<span v-if="r.restricted" class="tag bg-risk-bg text-risk">Restricted</span>
					</LinkRow>
				</div>
			</section>
		</div>
		<p v-if="!sops.length && !folders.length" class="hint">Nothing matches. Try another word.</p>
		<p class="hint mt-3">Every link opens the original in Google Drive. Opening it still depends on your Drive sharing.</p>
	</template>

	<!-- Tools we use -->
	<template v-else-if="tab === 'tools'">
		<p class="mb-4 max-w-[70ch] text-sm text-ink-2">Every tool we work with, what it is for, and where to learn it. Pin the ones you use to your Home page.</p>
		<div class="grid grid-cols-1 gap-3 sm:grid-cols-2 wide:grid-cols-3">
			<section v-for="t in library.data.tools" :key="t.tool_name" class="panel flex flex-col">
				<div class="flex items-start justify-between gap-2">
					<component :is="t.url ? 'a' : 'span'" v-bind="t.url ? { href: t.url, target: '_blank', rel: 'noopener' } : {}" class="font-display text-[17px] font-semibold text-ink no-underline hover:text-accent">
						{{ t.tool_name }}
						<Icon v-if="t.url" name="ext" class="ml-0.5 inline h-3.5 w-3.5 text-accent" />
					</component>
					<button
						class="grid h-8 w-8 flex-none place-items-center rounded-[9px]"
						:class="isPinned(t) ? 'bg-lav text-accent' : 'text-grey hover:bg-sunk'"
						:aria-pressed="isPinned(t)"
						:aria-label="isPinned(t) ? `Unpin ${t.tool_name} from Home` : `Pin ${t.tool_name} to Home`"
						@click="togglePin(`tool:${t.tool_name}`)"
					>
						<Icon name="pin" class="h-4 w-4" />
					</button>
				</div>
				<p class="mb-0 mt-1 text-sm text-ink-2">{{ t.purpose }}</p>
				<dl class="mb-0 mt-3 grid grid-cols-[auto_1fr] gap-x-3 gap-y-1 text-[13px]">
					<dt class="text-grey">Used by</dt>
					<dd class="m-0">{{ t.used_by || "Not set" }}</dd>
					<dt class="text-grey">We track</dt>
					<dd class="m-0">{{ t.tracked_measures || "To define" }}</dd>
				</dl>
				<div class="mt-auto pt-3">
					<a v-if="t.guide_url" :href="t.guide_url" target="_blank" rel="noopener" class="link">Open the guide</a>
					<span v-else class="hint">No guide yet</span>
				</div>
			</section>
		</div>
	</template>

	<!-- Who to ask -->
	<template v-else-if="tab === 'who-to-ask'">
		<p class="mb-4 max-w-[70ch] text-sm text-ink-2">Not sure who to go to? Find your question below, grouped by the kind of help you need.</p>
		<div class="grid grid-cols-1 items-start gap-3 sm:grid-cols-2 wide:grid-cols-3">
			<section v-for="group in helpGroups" :key="group.name" class="panel">
				<div class="mb-1 flex items-center gap-2.5">
					<span class="grid h-8 w-8 place-items-center rounded-[9px] bg-lav text-accent"><Icon :name="HELP_ICONS[group.name] || 'help'" class="h-[17px] w-[17px]" /></span>
					<h2 class="text-base">{{ group.name }}</h2>
				</div>
				<div v-for="h in group.items" :key="h.name" class="border-t border-line py-2.5 first:border-t-0">
					<p class="m-0 text-[13.5px] text-ink-2">{{ h.question }}</p>
					<div class="mt-1.5 flex items-center gap-2.5">
						<Avatar v-if="h.person_name" :name="h.person_name" :image="h.person_image" :size="30" />
						<span class="min-w-0">
							<b class="block text-sm">{{ h.person_name || h.role }}</b>
							<span class="hint block">{{ h.person_name ? h.role : "Person to be named" }}{{ h.how_to_reach ? ` · ${h.how_to_reach}` : "" }}</span>
						</span>
					</div>
				</div>
			</section>
		</div>
		<div class="mt-7 grid grid-cols-1 gap-5 nav:grid-cols-3">
			<div v-for="f in FAQ" :key="f[0]">
				<h3 class="text-base">{{ f[0] }}</h3>
				<p class="mb-0 mt-1.5 text-sm text-ink-2">{{ f[1] }}</p>
			</div>
		</div>
	</template>

	<!-- Request desk -->
	<template v-else>
		<p class="mb-4 max-w-[70ch] text-sm text-ink-2">Where each kind of request goes, and who picks it up. Each one opens the form, log or folder the request is made in.</p>
		<div v-if="requests.length" class="grid grid-cols-1 gap-3 sm:grid-cols-2 wide:grid-cols-3">
			<a
				v-for="r in requests"
				:key="r.label"
				:href="r.url"
				target="_blank"
				rel="noopener"
				class="panel flex flex-col no-underline hover:border-lav-2 hover:shadow"
			>
				<span class="mb-3 grid h-[38px] w-[38px] place-items-center rounded-[10px] bg-lav text-accent"><Icon :name="r.icon" class="h-[18px] w-[18px]" /></span>
				<h3 class="text-base">{{ r.label }}</h3>
				<p class="mb-0 mt-1.5 text-sm text-ink-2">{{ r.description }}</p>
				<span class="hint mt-2.5">{{ r.owner }}</span>
			</a>
		</div>
		<Empty v-else title="No requests set up yet">An admin lists a request by adding where it goes to a Who to ask topic in Desk.</Empty>
	</template>
</template>

<script setup>
import { computed, ref } from "vue"
import { call } from "frappe-ui"
import { boot } from "@/boot"
import { loadLibrary } from "@/data"
import Avatar from "@/components/Avatar.vue"
import Empty from "@/components/Empty.vue"
import Icon from "@/components/Icon.vue"
import LinkRow from "@/components/LinkRow.vue"
import Skeleton from "@/components/Skeleton.vue"

const props = defineProps({ tab: { type: String, default: null } })

const TABS = [
	{ key: "sops", label: "SOPs and templates" },
	{ key: "tools", label: "Tools we use" },
	{ key: "who-to-ask", label: "Who to ask" },
	{ key: "request-desk", label: "Request desk" },
]
const HELP_ICONS = {
	"People and HR": "people",
	"Approvals and direction": "star",
	"Equipment and the office": "camera",
	"Systems and tech": "grid",
	Money: "receipt",
	"Clients and delivery": "spark",
}
const FAQ = [
	["Where do I save my work?", "In the correctly named Drive folder for your department, linked to the ClickUp task."],
	["Why can't I open a folder?", "It may be restricted to the people who need it. Ask the owner listed next to the folder."],
	["WhatsApp or ASANTE ONE?", "WhatsApp for quick chat. Anything official, such as policies and requests, starts here."],
]

const tab = computed(() => (TABS.some((t) => t.key === props.tab) ? props.tab : "sops"))
const library = loadLibrary()
const query = ref("")

const matches = (...fields) => {
	const q = query.value.trim().toLowerCase()
	return !q || fields.join(" ").toLowerCase().includes(q)
}

const sops = computed(() =>
	library.data.policies.filter(
		(p) => ["How we work", "Culture"].includes(p.box) && !["Missing", "Archived"].includes(p.status) && matches(p.title, p.summary),
	),
)
const folders = computed(() => {
	const groups = new Map()
	for (const r of library.data.resources) {
		if (!matches(r.title, r.description, r.category, r.content_owner)) continue
		if (!groups.has(r.category)) groups.set(r.category, { category: r.category, items: [] })
		groups.get(r.category).items.push(r)
	}
	return [...groups.values()]
})

const helpGroups = computed(() => {
	const groups = new Map()
	for (const h of library.data.help) {
		if (!groups.has(h.help_group)) groups.set(h.help_group, { name: h.help_group, items: [] })
		groups.get(h.help_group).items.push(h)
	}
	return [...groups.values()]
})

const requests = computed(() => {
	const items = library.data.help
		.filter((h) => h.request_url)
		.map((h) => ({
			label: h.request_label || h.question,
			description: h.question,
			url: h.request_url,
			icon: HELP_ICONS[h.help_group] || "send",
			owner: `Goes to ${[h.role, h.person_name].filter(Boolean).join(", ")}`,
		}))
	if (boot.links.incident_template) {
		items.push({
			label: "Incident report",
			description: "Damaged, lost or faulty equipment, or an office problem",
			url: boot.links.incident_template,
			icon: "alert",
			owner: "Fill in the template and send it to the Company Assets Custodian",
		})
	}
	return items
})

const isPinned = (t) => boot.pins.includes(`tool:${t.tool_name}`)
async function togglePin(key) {
	boot.pins = await call("asante_one.api.home.toggle_pin", { key })
}
</script>

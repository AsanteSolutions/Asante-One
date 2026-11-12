<template>
	<div class="mb-[18px] mt-1 flex flex-col gap-4 nav:flex-row nav:items-end nav:justify-between">
		<div>
			<h1 class="page-title">Equipment</h1>
			<p class="page-lede">The equipment issued to you, the shoot kit in the office, and who has kit out on site.</p>
		</div>
		<div class="flex flex-wrap gap-2">
			<template v-if="links.check_out">
				<a :href="links.check_out" target="_blank" rel="noopener" class="btn btn-primary"><Icon name="box" class="h-4 w-4" /> Check out</a>
				<a :href="links.check_in" target="_blank" rel="noopener" class="btn"><Icon name="check" class="h-4 w-4" /> Check in</a>
			</template>
			<a v-if="links.incident_template" :href="links.incident_template" target="_blank" rel="noopener" class="btn">
				<Icon name="alert" class="h-4 w-4" /> Report a problem
			</a>
		</div>
	</div>

	<nav class="-mx-4 mb-6 flex gap-0.5 overflow-x-auto overflow-y-clip border-b border-line px-4 nav:mx-0 nav:px-0" aria-label="Equipment">
		<RouterLink
			v-for="t in tabs"
			:key="t.key"
			:to="`/equipment/${t.key}`"
			class="-mb-px whitespace-nowrap border-b-2 px-3.5 py-2.5 text-sm font-semibold no-underline"
			:class="tab === t.key ? 'border-accent-bg text-ink' : 'border-transparent text-grey hover:text-ink'"
			:aria-current="tab === t.key ? 'page' : undefined"
		>
			{{ t.label }}
		</RouterLink>
	</nav>

	<p v-if="equipment.error" class="hint">This page could not load. Refresh the page to try again.</p>
	<Skeleton v-else-if="!d" :rows="6" />

	<!-- My equipment -->
	<div v-else-if="tab === 'mine'" class="grid grid-cols-1 items-start gap-4 nav:grid-cols-2">
		<section class="panel">
			<h2 class="text-lg">Issued to you</h2>
			<div v-if="d.assets.length" class="mt-1.5 flex flex-col">
				<div v-for="a in d.assets" :key="a.name" class="flex items-center gap-3.5 border-t border-line px-1 py-3 first:border-t-0">
					<span class="grid h-9 w-9 flex-none place-items-center rounded-[11px] bg-sunk text-accent"><Icon name="work" class="h-[18px] w-[18px]" /></span>
					<span class="min-w-0 flex-1">
						<span class="block font-semibold">{{ a.asset_name }}</span>
						<span class="hint block">{{ [a.item_name !== a.asset_name && a.item_name, a.name, a.location].filter(Boolean).join(" · ") }}</span>
					</span>
					<span v-if="a.status === 'Draft'" class="tag bg-warn-bg text-warn">Not confirmed</span>
				</div>
			</div>
			<p v-else class="mb-0 mt-2 text-sm text-ink-2">
				Nothing is issued to you yet. If you have a company laptop or phone, ask the Company Assets Custodian to record it.
			</p>
		</section>

		<section v-if="d.configured" class="panel">
			<h2 class="text-lg">Shoot kit you have out</h2>
			<div v-if="d.kit.length" class="mt-1.5 flex flex-col">
				<KitRow v-for="h in d.kit" :key="h.item_code" :item="h" :qty="h.qty">
					{{ outSince(h) }}
				</KitRow>
				<p class="hint mb-0 mt-3">Bringing it back? Check it in, so it shows as available again.</p>
			</div>
			<p v-else class="mb-0 mt-2 text-sm text-ink-2">
				No shoot kit is out in your name.
				<RouterLink to="/equipment/kit" class="link">See what is available</RouterLink>
			</p>
		</section>
	</div>

	<Empty v-else-if="!d.configured" title="Equipment is not set up yet">
		<template v-if="boot.is_admin">Choose the Check Out and Check In stock entry types and the office and site warehouses in One Settings.</template>
		<template v-else>The Company Assets Custodian is setting it up. Until then, ask them for kit.</template>
	</Empty>

	<!-- Available kit -->
	<template v-else-if="tab === 'kit'">
		<KitFilters v-model:query="query" v-model:group="group" :groups="groups" placeholder="Search kit" />
		<section v-if="kit.length" class="panel py-1.5 nav:py-1.5">
			<KitRow v-for="item in kit" :key="item.item_code" :item="item">
				{{ item.item_group }}
				<template #right>
					<span v-if="item.available > 0" class="tag bg-ok-bg text-ok">{{ count(item.available) }} available</span>
					<span v-else class="tag bg-warn-bg text-warn">All out</span>
					<span v-if="item.out > 0" class="hint">{{ count(item.out) }} on site</span>
				</template>
			</KitRow>
		</section>
		<p v-else-if="d.items.length" class="hint">Nothing matches. Try another word.</p>
		<Empty v-else title="No kit in the office yet">Kit shows here once it is received into the office warehouse in ERPNext.</Empty>
		<p class="hint mt-3">From ERPNext stock. New kit shows here once it is received into the office.</p>
	</template>

	<!-- Out now -->
	<template v-else-if="tab === 'out'">
		<div v-if="d.people.length || d.unnamed.length" class="grid grid-cols-1 items-start gap-4 nav:grid-cols-2">
			<section v-for="p in d.people" :key="p.employee" class="panel">
				<div class="flex items-center gap-3">
					<Avatar :name="p.name" :image="p.image" :size="36" />
					<span class="min-w-0">
						<h2 class="text-base">{{ p.name }}</h2>
						<span class="hint">{{ itemCount(p.items) }}</span>
					</span>
				</div>
				<div class="mt-2 flex flex-col">
					<KitRow v-for="h in p.items" :key="h.item_code" :item="h" :qty="h.qty">{{ outSince(h) }}</KitRow>
				</div>
			</section>
			<section v-if="d.unnamed.length" class="panel">
				<h2 class="text-base">Nobody named</h2>
				<p class="hint mb-0 mt-0.5">On site, but the check out does not say who took it. The Company Assets Custodian can find out.</p>
				<div class="mt-2 flex flex-col">
					<KitRow v-for="item in d.unnamed" :key="item.item_code" :item="item" :qty="item.qty">{{ item.item_group }}</KitRow>
				</div>
			</section>
		</div>
		<Empty v-else title="Nothing is out on site">All the shoot kit is in the office.</Empty>
	</template>

	<!-- Full register, for the custodian -->
	<template v-else>
		<dl class="mb-6 grid grid-cols-2 gap-x-5 gap-y-4 sm:grid-cols-3 wide:grid-cols-6">
			<div v-for="t in totals" :key="t.label" class="border-t-2 border-line pt-3">
				<dt class="text-xs font-semibold text-grey">{{ t.label }}</dt>
				<dd class="m-0 mt-1 font-display text-[26px] font-semibold leading-tight" :class="t.warn && t.value ? 'text-risk' : ''">{{ count(t.value) }}</dd>
			</div>
		</dl>

		<div class="grid grid-cols-1 items-start gap-4 nav:grid-cols-[minmax(0,1.5fr)_minmax(0,1fr)]">
			<div class="flex min-w-0 flex-col gap-4">
				<KitFilters v-model:query="query" v-model:group="group" :groups="groups" placeholder="Search the register" />
				<section class="panel py-1.5 nav:py-1.5">
					<KitRow v-for="item in register" :key="item.item_code" :item="item">
						{{ item.holders.length ? `With ${item.holders.map((h) => `${h.name} (${count(h.qty)})`).join(", ")}` : item.item_group }}
						<template #right>
							<span class="hint whitespace-nowrap">{{ count(item.available) }} in office</span>
							<span class="hint whitespace-nowrap" :class="item.out > 0 && 'font-semibold text-ink'">{{ count(item.out) }} on site</span>
						</template>
					</KitRow>
					<p v-if="!register.length" class="hint my-3">Nothing matches. Try another word.</p>
				</section>
			</div>

			<div class="flex min-w-0 flex-col gap-4">
				<section class="panel">
					<h2 class="text-lg">In ERPNext</h2>
					<div class="mt-1.5 flex flex-col">
						<LinkRow v-for="l in deskLinks" :key="l.title" :href="l.href" :icon="l.icon" :title="l.title" :subtitle="l.subtitle" />
					</div>
				</section>

				<section class="panel">
					<h2 class="text-lg">Latest check outs and check ins</h2>
					<div v-if="d.recent.length" class="mt-1.5 flex flex-col">
						<a
							v-for="e in d.recent"
							:key="e.name"
							:href="`/desk/stock-entry/${e.name}`"
							target="_blank"
							rel="noopener"
							class="group flex items-start justify-between gap-3 border-t border-line py-2.5 no-underline first:border-t-0"
						>
							<span class="min-w-0">
								<span class="block text-sm font-semibold group-hover:text-accent">{{ e.kind }}: {{ e.champion || "nobody named" }}</span>
								<span class="hint block">{{ [formatDate(e.posting_date), `${count(e.qty)} item${e.qty === 1 ? "" : "s"}`, e.purpose].filter(Boolean).join(" · ") }}</span>
							</span>
							<span v-if="!e.champion" class="tag bg-risk-bg text-risk">No name</span>
						</a>
					</div>
					<p v-else class="hint mb-0 mt-2">No check outs or check ins yet.</p>
				</section>

				<section class="panel">
					<h2 class="text-lg">Personal kit</h2>
					<div v-if="d.assets.length" class="mt-1.5 flex flex-col">
						<a
							v-for="a in d.assets"
							:key="a.name"
							:href="`/desk/asset/${a.name}`"
							target="_blank"
							rel="noopener"
							class="group flex items-start justify-between gap-3 border-t border-line py-2.5 no-underline first:border-t-0"
						>
							<span class="min-w-0">
								<span class="block text-sm font-semibold group-hover:text-accent">{{ a.asset_name }}</span>
								<span class="hint block">{{ [a.name, a.location].filter(Boolean).join(" · ") }}</span>
							</span>
							<span v-if="a.custodian_name" class="hint whitespace-nowrap">{{ a.custodian_name }}</span>
							<span v-else class="tag bg-warn-bg text-warn">Not issued</span>
						</a>
					</div>
					<p v-else class="hint mb-0 mt-2">No laptops or phones are recorded as Assets yet.</p>
				</section>
			</div>
		</div>
	</template>
</template>

<script setup>
import { computed, ref, watch } from "vue"
import { createResource } from "frappe-ui"
import { boot } from "@/boot"
import { formatDate } from "@/utils/dates"
import { count, itemCount, outSince } from "@/utils/equipment"
import Avatar from "@/components/Avatar.vue"
import Empty from "@/components/Empty.vue"
import Icon from "@/components/Icon.vue"
import KitFilters from "@/components/KitFilters.vue"
import KitRow from "@/components/KitRow.vue"
import LinkRow from "@/components/LinkRow.vue"
import Skeleton from "@/components/Skeleton.vue"

const props = defineProps({ tab: { type: String, default: null } })

const links = boot.links
const tabs = computed(() =>
	[
		{ key: "mine", label: "My equipment" },
		{ key: "kit", label: "Available kit" },
		{ key: "out", label: "Out now" },
		boot.is_custodian && { key: "register", label: "Full register" },
	].filter(Boolean),
)
const tab = computed(() => (tabs.value.some((t) => t.key === props.tab) ? props.tab : "mine"))

// One resource per tab, so switching back shows the last data straight away and refreshes it
const resources = {}
const equipment = computed(() => {
	resources[tab.value] ||= createResource({ url: "asante_one.api.equipment.get_equipment", params: { tab: tab.value } })
	return resources[tab.value]
})
watch(equipment, (resource) => resource.fetch(), { immediate: true })
const d = computed(() => equipment.value.data)

const query = ref("")
const group = ref("All")
watch(tab, () => {
	query.value = ""
	group.value = "All"
})

const groups = computed(() => ["All", ...new Set((d.value?.items || []).map((item) => item.item_group))])
const filtered = computed(() => {
	const q = query.value.trim().toLowerCase()
	return (d.value?.items || []).filter(
		(item) =>
			(group.value === "All" || item.item_group === group.value) &&
			(!q || [item.item_name, item.item_code, item.item_group].join(" ").toLowerCase().includes(q)),
	)
})
// Available kit lists what is in the office first; the register keeps ERPNext's order by group
const kit = computed(() => [...filtered.value].sort((a, b) => (b.available > 0) - (a.available > 0)))
const register = filtered

const totals = computed(() => {
	const t = d.value.totals
	return [
		{ label: "Kinds of kit", value: t.items },
		{ label: "In the office", value: t.available },
		{ label: "On site", value: t.out },
		{ label: "On site, nobody named", value: t.unnamed, warn: true },
		{ label: "Personal kit", value: t.assets },
		{ label: "Personal kit not issued", value: t.unassigned, warn: true },
	]
})

const deskLinks = [
	{ title: "Stock balance", subtitle: "Every item by warehouse", icon: "grid", href: "/desk/query-report/Stock Balance" },
	{ title: "Check outs and check ins", subtitle: "Stock entries", icon: "box", href: "/desk/stock-entry" },
	{ title: "Items", subtitle: "Add new kit", icon: "camera", href: "/desk/item" },
	{ title: "Assets", subtitle: "Laptops and phones, and who has them", icon: "work", href: "/desk/asset" },
	links.purchase_list && { title: "Purchase list", subtitle: "Equipment to buy", icon: "receipt", href: links.purchase_list },
].filter(Boolean)
</script>

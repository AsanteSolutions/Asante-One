<template>
	<div class="mb-[26px] mt-1">
		<h1 class="page-title">People and HR</h1>
		<p class="page-lede">Every HR action in plain language. Each one opens the right place in Frappe HR on AsantePower.</p>
	</div>

	<div class="mb-7 grid grid-cols-1 gap-2 sm:grid-cols-2 wide:grid-cols-4">
		<a
			v-for="action in top"
			:key="action.key"
			:href="hrHref(action)"
			target="_blank"
			rel="noopener"
			class="flex items-center gap-3 rounded-[14px] border border-line bg-surface px-3.5 py-3 no-underline hover:border-lav-2 hover:shadow"
		>
			<span class="grid h-9 w-9 flex-none place-items-center rounded-[10px] bg-lav text-accent"><Icon :name="action.icon" class="h-[18px] w-[18px]" /></span>
			<span>
				<b class="block text-[14.5px] font-semibold leading-tight">{{ action.label }}</b>
				<span class="hint">Frappe HR</span>
			</span>
		</a>
	</div>

	<div class="grid grid-cols-1 gap-3 sm:grid-cols-2 wide:grid-cols-4">
		<section v-for="mod in modules" :key="mod.name" class="panel">
			<div class="mb-2 flex items-center gap-2.5">
				<span class="grid h-8 w-8 place-items-center rounded-[9px] bg-sunk text-accent"><Icon :name="mod.icon" class="h-[17px] w-[17px]" /></span>
				<h2 class="text-base">{{ mod.name }}</h2>
			</div>
			<ul class="m-0 list-none p-0">
				<li v-for="action in mod.actions" :key="action.key">
					<a
						:href="hrHref(action)"
						target="_blank"
						rel="noopener"
						class="flex items-center justify-between gap-2 border-t border-line py-2 text-[14px] no-underline first:border-t-0 hover:text-accent"
					>
						<span>{{ action.label }}</span>
						<!-- A note for admins checking routes; employees just see the link -->
						<span v-if="!action.verified && boot.is_admin" class="tag bg-warn-bg text-warn">Route to verify</span>
						<span v-else class="text-grey" aria-hidden="true">›</span>
					</a>
				</li>
			</ul>
		</section>
	</div>

	<div class="mt-8 grid grid-cols-1 gap-7 nav:grid-cols-3">
		<section>
			<h2 class="text-[19px]">Before you apply</h2>
			<p class="hint mb-2 mt-1">Read the rules first. The document in Drive is always the official one.</p>
			<p v-if="library.error" class="hint">This list could not load. Refresh the page to try again.</p>
			<p v-else-if="library.loading && !library.data" class="hint">Loading…</p>
			<div class="flex flex-col">
				<LinkRow v-for="p in policies" :key="p.name" :to="`/policies/${p.name}`" icon="book" :title="p.title">
					<StatusTag :status="p.status" />
				</LinkRow>
			</div>
		</section>
		<section>
			<h2 class="text-[19px]">Growing here</h2>
			<p class="hint mb-2 mt-1">Scopes of work, performance and learning.</p>
			<div class="flex flex-col">
				<LinkRow v-for="r in growing" :key="r.name" :href="r.url" icon="folder" :title="r.title" :subtitle="r.description">
					<span v-if="r.restricted" class="tag bg-risk-bg text-risk">Restricted</span>
				</LinkRow>
			</div>
		</section>
		<section>
			<h2 class="text-[19px]">On your phone</h2>
			<p class="mt-1 text-sm text-ink-2">
				The Frappe HR app is built for leave, check in, expenses and payslips. On a phone, ASANTE ONE opens HR actions there.
			</p>
			<a class="btn mt-3.5" :href="boot.links.hrms" target="_blank" rel="noopener"><Icon name="ext" class="h-4 w-4" /> Open the Frappe HR app</a>
		</section>
	</div>
</template>

<script setup>
import { computed } from "vue"
import { boot, hrAction } from "@/boot"
import { loadLibrary } from "@/data"
import { hrHref } from "@/utils/actions"
import Icon from "@/components/Icon.vue"
import LinkRow from "@/components/LinkRow.vue"
import StatusTag from "@/components/StatusTag.vue"

const library = loadLibrary()

// The four everyone needs most, then every module in the order set in Desk
const top = computed(() => ["leave", "wfh", "balance", "myleave"].map(hrAction).filter(Boolean))

const modules = computed(() => {
	const byName = new Map()
	for (const action of boot.hr_actions) {
		if (!byName.has(action.module)) byName.set(action.module, { name: action.module, icon: action.icon, actions: [] })
		byName.get(action.module).actions.push(action)
	}
	return [...byName.values()]
})

const policies = computed(() =>
	(library.data?.policies || []).filter((p) => p.box === "People and HR" && p.status !== "Archived"),
)
const growing = computed(() =>
	(library.data?.resources || []).filter((r) => ["People and HR", "Learning"].includes(r.category)),
)
</script>

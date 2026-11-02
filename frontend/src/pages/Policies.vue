<template>
	<div class="mb-[22px] mt-1">
		<h1 class="page-title">Policies and procedures</h1>
		<p class="page-lede">The approved version of every rule, with its owner and review date. The document in Drive is always the official one.</p>
	</div>

	<p v-if="library.error" class="hint">Policies could not load. Refresh the page to try again.</p>
	<template v-else-if="library.data">
		<div v-if="missing" class="mb-5 flex items-start gap-3 rounded-[14px] bg-risk-bg px-4 py-3 text-sm text-risk">
			<Icon name="alert" class="mt-0.5 h-4 w-4 flex-none" />
			<span><b>{{ missing }} {{ missing === 1 ? "policy is" : "policies are" }} not in Drive yet.</b> They are listed with their owner so the gap is visible.</span>
		</div>

		<section class="mb-7" aria-labelledby="boxes">
			<h2 id="boxes" class="mb-3 text-[19px]">Policy folders</h2>
			<div class="grid grid-cols-2 gap-2 sm:grid-cols-3 wide:grid-cols-4">
				<component
					:is="box.drive_folder_url ? 'a' : 'div'"
					v-for="box in library.data.boxes"
					:key="box.name"
					v-bind="box.drive_folder_url ? { href: box.drive_folder_url, target: '_blank', rel: 'noopener' } : {}"
					class="flex min-h-[64px] items-center gap-[11px] rounded-[14px] border border-line bg-surface px-3 py-2.5 no-underline"
					:class="box.drive_folder_url ? 'hover:border-lav-2 hover:shadow' : ''"
				>
					<span class="grid h-8 w-8 flex-none place-items-center rounded-[9px] bg-lav text-accent"><Icon :name="box.icon" class="h-[17px] w-[17px]" /></span>
					<span class="min-w-0">
						<b class="block text-[13.5px] font-semibold leading-tight">{{ box.title }}</b>
						<small class="block text-[11.5px] text-grey">{{ box.drive_folder_url ? box.drive_folder_name || "Google Drive" : "Folder link to add" }}</small>
					</span>
				</component>
			</div>
		</section>

		<div class="mb-3.5 flex flex-col gap-3 nav:flex-row nav:items-center">
			<input v-model="query" class="input nav:max-w-[280px]" placeholder="Filter policies" aria-label="Filter policies" />
			<div class="-mx-4 flex gap-1.5 overflow-x-auto px-4 nav:mx-0 nav:flex-wrap nav:px-0" role="group" aria-label="Policy folder">
				<button v-for="name in filters" :key="name" :class="['chip', box === name && 'chip-on']" :aria-pressed="box === name" @click="box = name">
					{{ name }}
				</button>
			</div>
		</div>

		<section class="panel py-1.5 nav:py-1.5">
			<RouterLink
				v-for="p in shown"
				:key="p.name"
				:to="`/policies/${p.name}`"
				class="group flex items-start justify-between gap-3 border-t border-line py-3 no-underline first:border-t-0"
			>
				<span class="min-w-0">
					<span class="block font-semibold group-hover:text-accent">{{ p.title }}</span>
					<span v-if="p.summary" class="mt-0.5 block text-[13px] text-ink-2">{{ p.summary }}</span>
					<span class="mt-1 flex flex-wrap gap-x-3.5 text-[12.5px] text-grey">
						<span>{{ p.box }}</span>
						<span v-if="p.policy_owner">Owner: {{ p.policy_owner }}</span>
						<span v-if="p.updated_on">Updated {{ formatDate(p.updated_on) }}</span>
						<span v-if="p.next_review">Review {{ formatDate(p.next_review) }}</span>
					</span>
				</span>
				<StatusTag :status="p.status" />
			</RouterLink>
			<p v-if="!shown.length" class="hint py-4">Nothing matches. Try another word or folder.</p>
		</section>
	</template>
	<div v-else class="flex flex-col gap-3" aria-busy="true">
		<div v-for="n in 5" :key="n" class="h-12 animate-pulse rounded-lg bg-sunk" />
	</div>
</template>

<script setup>
import { computed, ref } from "vue"
import { loadLibrary } from "@/data"
import { formatDate } from "@/utils/dates"
import Icon from "@/components/Icon.vue"
import StatusTag from "@/components/StatusTag.vue"

const library = loadLibrary()
const query = ref("")
const box = ref("All")

const policies = computed(() => library.data?.policies || [])
const missing = computed(() => policies.value.filter((p) => p.status === "Missing").length)
const filters = computed(() => ["All", ...new Set(policies.value.map((p) => p.box))])
const shown = computed(() => {
	const q = query.value.trim().toLowerCase()
	return policies.value.filter(
		(p) =>
			(box.value === "All" || p.box === box.value) &&
			(!q || [p.title, p.summary, p.box, p.policy_owner].join(" ").toLowerCase().includes(q)),
	)
})
</script>

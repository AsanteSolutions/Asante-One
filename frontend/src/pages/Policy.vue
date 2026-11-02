<template>
	<div v-if="policy.data" :key="policy.data.name">
		<div class="mb-6 mt-1 flex flex-col gap-4 nav:flex-row nav:items-end nav:justify-between">
			<div>
				<div class="mb-2.5 flex flex-wrap gap-1.5">
					<StatusTag :status="p.status" />
					<span class="tag border border-line bg-sunk text-ink-2">{{ p.box }}</span>
				</div>
				<h1 class="page-title">{{ p.title }}</h1>
				<p v-if="p.summary" class="page-lede">{{ p.summary }}</p>
			</div>
			<a v-if="p.drive_url" :href="p.drive_url" target="_blank" rel="noopener" class="btn btn-primary self-start nav:self-auto">
				<Icon name="ext" class="h-4 w-4" /> Open the official document
			</a>
		</div>

		<div class="grid grid-cols-1 items-start gap-4 nav:grid-cols-[minmax(0,1.6fr)_minmax(0,1fr)]">
			<section class="panel">
				<div v-if="p.status === 'Archived'" class="mb-4 flex gap-2.5 rounded-xl bg-sunk p-3 text-sm">
					<Icon name="alert" class="mt-0.5 h-4 w-4 flex-none text-grey" />
					<span><b>Archived.</b> Kept for history. Use the current version listed under Related.</span>
				</div>
				<template v-if="p.takeaways.length">
					<h2 class="text-lg">What it means for you</h2>
					<ul class="mb-0 mt-3.5 pl-5">
						<li v-for="(t, i) in p.takeaways" :key="i" class="mb-2">{{ t }}</li>
					</ul>
					<p class="hint mt-4">Summary written by the policy owner. If it ever disagrees with the official document, the document wins.</p>
				</template>
				<div v-else-if="!p.drive_url" class="rounded-[14px] border-[1.5px] border-dashed border-line-2 bg-canvas p-4 text-sm text-ink-2">
					This policy is not in Drive yet. {{ p.policy_owner || "Its owner" }} owns it; until it is published, ask them directly.
				</div>
				<p v-else class="text-sm text-ink-2">Open the official document for the full policy.</p>
			</section>

			<div class="flex flex-col gap-4">
				<section class="panel">
					<h3 class="text-base">Details</h3>
					<dl class="mb-0 mt-3 grid grid-cols-[auto_1fr] gap-x-4 gap-y-2 text-sm">
						<dt class="text-grey">Owner</dt>
						<dd class="m-0">{{ p.policy_owner || "Not set" }}</dd>
						<dt class="text-grey">Status</dt>
						<dd class="m-0">{{ STATUS[p.status]?.label || p.status }}</dd>
						<dt class="text-grey">Last updated</dt>
						<dd class="m-0">{{ formatDate(p.updated_on) || "Not yet" }}</dd>
						<dt class="text-grey">Next review</dt>
						<dd class="m-0">{{ formatDate(p.next_review) || "Not set" }}</dd>
						<dt class="text-grey">Lives in</dt>
						<dd class="m-0">{{ p.drive_url ? "Google Drive" : "Nowhere yet" }}</dd>
					</dl>
				</section>
				<section v-if="p.related.length" class="panel">
					<h3 class="text-base">Related</h3>
					<div class="mt-1 flex flex-col">
						<LinkRow v-for="r in p.related" :key="r.name" :to="`/policies/${r.name}`" icon="book" :title="r.title">
							<StatusTag :status="r.status" />
						</LinkRow>
					</div>
				</section>
			</div>
		</div>
	</div>

	<div v-else-if="policy.error" class="mx-auto my-10 max-w-[560px] rounded-[14px] border-[1.5px] border-dashed border-line-2 bg-canvas p-5 text-center text-sm text-ink-2">
		<b class="mb-1 block text-ink">This policy could not be found</b>
		<RouterLink to="/policies" class="link">See all policies</RouterLink>
	</div>
	<div v-else class="flex flex-col gap-3" aria-busy="true">
		<div class="h-10 w-2/3 animate-pulse rounded-lg bg-sunk" />
		<div class="h-40 animate-pulse rounded-[20px] bg-sunk" />
	</div>
</template>

<script setup>
import { computed, watch } from "vue"
import { createResource } from "frappe-ui"
import { STATUS } from "@/data"
import { formatDate } from "@/utils/dates"
import Icon from "@/components/Icon.vue"
import LinkRow from "@/components/LinkRow.vue"
import StatusTag from "@/components/StatusTag.vue"

const props = defineProps({ name: { type: String, required: true } })

const policy = createResource({ url: "asante_one.api.library.get_policy" })
const p = computed(() => policy.data)

watch(
	() => props.name,
	(name) => {
		policy.reset()
		policy.fetch({ name })
	},
	{ immediate: true },
)

watch(p, (data) => data && (document.title = `${data.title} · ASANTE ONE`))
</script>

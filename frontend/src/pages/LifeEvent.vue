<template>
	<div v-if="e">
		<div class="mb-6 mt-1 flex flex-col gap-4 nav:flex-row nav:items-end nav:justify-between">
			<div>
				<div class="mb-2.5 flex flex-wrap gap-1.5">
					<span :class="['tag', closure ? KINDS.closure : KINDS.company]">{{ e.category }}</span>
					<span v-if="e.past" class="tag border border-line bg-sunk text-ink-2">Past event</span>
				</div>
				<h1 class="page-title">{{ e.title }}</h1>
				<p class="page-lede">{{ when }}</p>
			</div>
			<a v-if="e.photo_folder_url" :href="e.photo_folder_url" target="_blank" rel="noopener" class="btn btn-primary self-start nav:self-auto">
				<Icon name="folder" class="h-4 w-4" /> Open the photos
			</a>
		</div>

		<div class="grid grid-cols-1 items-start gap-4 nav:grid-cols-[minmax(0,1.6fr)_minmax(0,1fr)]">
			<section class="panel">
				<img v-if="e.cover_image" :src="e.cover_image" :alt="e.title" class="mb-4 block aspect-[16/9] w-full rounded-[14px] object-cover" />
				<h2 class="text-lg">About</h2>
				<div v-if="e.description" class="mt-2.5 text-[15px] text-ink-2 [&_a]:text-accent" v-html="e.description" />
				<p v-else class="hint mt-2.5">No details were added to this event.</p>
				<Empty v-if="e.past && !e.photo_folder_url" class="mt-4">
					Photo folder link to add. An admin adds it to the event in Desk, and it opens from here.
				</Empty>
			</section>
			<section class="panel">
				<h3 class="text-base">Details</h3>
				<dl class="mb-0 mt-3 grid grid-cols-[auto_1fr] gap-x-4 gap-y-2 text-sm">
					<dt class="text-grey">When</dt>
					<dd class="m-0">{{ when }}</dd>
					<dt class="text-grey">Source</dt>
					<dd class="m-0">Company holiday calendar</dd>
				</dl>
			</section>
		</div>
	</div>

	<Empty v-else-if="event.error" class="mx-auto my-10 text-center" title="This event could not be found">
		<RouterLink to="/life" class="link">Back to Life at Asante Solutions</RouterLink>
	</Empty>
	<Skeleton v-else />
</template>

<script setup>
import { computed, watch } from "vue"
import { createResource } from "frappe-ui"
import { KINDS } from "@/data"
import { shortDay, timeOf } from "@/utils/dates"
import Empty from "@/components/Empty.vue"
import Icon from "@/components/Icon.vue"
import Skeleton from "@/components/Skeleton.vue"

const props = defineProps({ name: { type: String, required: true } })

const event = createResource({ url: "asante_one.api.life.get_event" })
const e = computed(() => event.data)
const closure = computed(() => ["Shutdown", "Closure", "Company holiday"].includes(e.value?.category))

watch(
	() => props.name,
	(name) => {
		event.reset()
		event.fetch({ name })
	},
	{ immediate: true },
)
watch(e, (data) => data && (document.title = `${data.title} · ASANTE ONE`))

const when = computed(() => {
	const start = e.value.starts_on.slice(0, 10)
	const end = e.value.ends_on?.slice(0, 10)
	if (end && end !== start) return `${shortDay(start)} to ${shortDay(end)} ${end.slice(0, 4)}`
	const time = e.value.all_day ? "" : `, ${timeOf(e.value.starts_on)}`
	return `${shortDay(start)} ${start.slice(0, 4)}${time}`
})
</script>

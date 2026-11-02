<template>
	<div class="mb-[22px] mt-1 flex flex-col gap-4 nav:flex-row nav:items-end nav:justify-between">
		<div>
			<h1 class="page-title">Life at Asante Solutions</h1>
			<p class="page-lede">Holidays, closures, company events, birthdays and memories. Dates come from the company holiday calendar, never anyone's personal calendar.</p>
		</div>
		<div class="flex gap-1.5" role="group" aria-label="View">
			<button :class="['chip', view === 'list' && 'chip-on']" :aria-pressed="view === 'list'" @click="setQuery({ view: undefined })">List</button>
			<button :class="['chip', view === 'month' && 'chip-on']" :aria-pressed="view === 'month'" @click="setQuery({ view: 'month' })">Month</button>
		</div>
	</div>

	<template v-if="view === 'list'">
		<div class="-mx-4 mb-5 flex gap-1.5 overflow-x-auto px-4 nav:mx-0 nav:px-0" role="group" aria-label="Show">
			<button
				v-for="f in FILTERS"
				:key="f.key"
				:class="['chip', filter === f.key && 'chip-on']"
				:aria-pressed="filter === f.key"
				@click="setQuery({ show: f.key === 'upcoming' ? undefined : f.key })"
			>
				{{ f.label }}
			</button>
		</div>

		<template v-if="filter === 'memories'">
			<p v-if="memories.error" class="hint">Memories could not load. Refresh the page to try again.</p>
			<div v-else-if="memories.data?.length" class="grid grid-cols-1 gap-3 sm:grid-cols-2 wide:grid-cols-3">
				<RouterLink
					v-for="m in memories.data"
					:key="m.name"
					:to="`/life/${m.name}`"
					class="group overflow-hidden rounded-[18px] border border-line bg-surface no-underline hover:shadow"
				>
					<div class="grid aspect-[16/9] place-items-center bg-lav text-accent">
						<img v-if="m.cover_image" :src="m.cover_image" :alt="m.title" class="h-full w-full object-cover" loading="lazy" />
						<Icon v-else name="camera" class="h-8 w-8" />
					</div>
					<div class="p-4">
						<b class="block group-hover:text-accent">{{ m.title }}</b>
						<span class="hint block">{{ formatDate(m.date) }}</span>
						<p v-if="m.summary" class="mb-0 mt-1.5 text-[13px] text-ink-2">{{ m.summary }}</p>
					</div>
				</RouterLink>
			</div>
			<Empty v-else-if="memories.data" title="No memories yet">
				Past company events show here, with their photos once a photo folder is added to the event.
			</Empty>
			<Skeleton v-else />
		</template>

		<div v-else class="grid grid-cols-1 items-start gap-7 nav:grid-cols-[minmax(0,1.6fr)_minmax(0,1fr)]">
			<section class="panel" aria-label="Dates">
				<p v-if="upcoming.error" class="hint">Dates could not load. Refresh the page to try again.</p>
				<Skeleton v-else-if="!upcoming.data" />
				<p v-else-if="!listed.length" class="hint">Nothing in the next six months.</p>
				<template v-for="group in grouped" v-else :key="group.month">
					<h2 class="mb-1 mt-5 text-[15px] text-grey first:mt-0">{{ monthTitle(group.month) }}</h2>
					<DateRow v-for="item in group.items" :key="`${item.date}-${item.title}`" :item="item" />
				</template>
			</section>
			<section v-if="planning.length" aria-labelledby="planning">
				<h2 id="planning" class="text-[19px]">Planning an event?</h2>
				<div class="mt-2 flex flex-col">
					<LinkRow v-for="r in planning" :key="r.name" :href="r.url" icon="cake" :title="r.title" :subtitle="r.description" />
				</div>
			</section>
		</div>
	</template>

	<template v-else>
		<div class="mb-3.5 flex items-center justify-between gap-3">
			<h2 class="text-[22px]">{{ monthTitle(month) }}</h2>
			<div class="flex gap-1.5">
				<button class="btn px-2.5" aria-label="Previous month" @click="setQuery({ month: shiftMonth(month, -1) })"><Icon name="left" class="h-4 w-4" /></button>
				<button class="btn" @click="setQuery({ month: undefined })">Today</button>
				<button class="btn px-2.5" aria-label="Next month" @click="setQuery({ month: shiftMonth(month, 1) })"><Icon name="right" class="h-4 w-4" /></button>
			</div>
		</div>

		<div class="overflow-hidden rounded-2xl border border-line bg-surface" :aria-busy="monthDates.loading">
			<div class="grid grid-cols-7 border-b border-line bg-sunk text-center text-xs font-semibold text-grey">
				<div v-for="d in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']" :key="d" class="py-2">{{ d }}</div>
			</div>
			<div v-for="week in weeks" :key="week[0]" class="grid grid-cols-7 border-b border-line last:border-b-0">
				<div
					v-for="day in week"
					:key="day"
					class="min-h-[58px] min-w-0 border-r border-line p-1 last:border-r-0 nav:min-h-[96px] nav:p-1.5"
					:class="day.slice(0, 7) !== month ? 'bg-canvas text-grey' : ''"
				>
					<span
						class="mb-1 grid h-6 w-6 place-items-center rounded-full text-xs font-semibold"
						:class="day === today ? 'bg-accent-bg text-white' : ''"
					>{{ Number(day.slice(8)) }}</span>
					<template v-for="item in onDay(day)" :key="item.title">
						<RouterLink
							v-if="item.to"
							:to="item.to"
							:title="item.title"
							:class="['mb-0.5 hidden truncate rounded-md px-1.5 text-[11.5px] font-semibold no-underline nav:block', KINDS[item.kind]]"
						>{{ item.title }}</RouterLink>
						<span v-else :title="item.title" :class="['mb-0.5 hidden truncate rounded-md px-1.5 text-[11.5px] font-semibold nav:block', KINDS[item.kind]]">{{ item.title }}</span>
						<span :class="['mr-0.5 inline-block h-[7px] w-[7px] rounded-full nav:hidden', DOTS[item.kind]]" aria-hidden="true" />
					</template>
				</div>
			</div>
		</div>

		<section class="panel mt-4 nav:hidden" aria-label="This month">
			<p v-if="monthDates.data && !inMonth.length" class="hint">Nothing this month.</p>
			<DateRow v-for="item in inMonth" :key="`${item.date}-${item.title}`" :item="item" />
		</section>
	</template>
</template>

<script setup>
import { computed, watch } from "vue"
import { useRoute, useRouter } from "vue-router"
import { createResource } from "frappe-ui"
import { DOTS, KINDS, loadLibrary } from "@/data"
import { addDays, formatDate, monthTitle, monthWeeks, shiftMonth, todayISO } from "@/utils/dates"
import DateRow from "@/components/DateRow.vue"
import Empty from "@/components/Empty.vue"
import Icon from "@/components/Icon.vue"
import LinkRow from "@/components/LinkRow.vue"
import Skeleton from "@/components/Skeleton.vue"

const FILTERS = [
	{ key: "upcoming", label: "Upcoming", kinds: null },
	{ key: "celebrations", label: "Birthdays and anniversaries", kinds: ["birthday", "anniversary"] },
	{ key: "days-off", label: "Days off", kinds: ["public_holiday", "closure"] },
	{ key: "memories", label: "Memories" },
]

const route = useRoute()
const router = useRouter()
const today = todayISO()

// The view, filter and month live in the address, so Back and shared links keep them
const view = computed(() => (route.query.view === "month" ? "month" : "list"))
const filter = computed(() => (FILTERS.some((f) => f.key === route.query.show) ? route.query.show : "upcoming"))
const month = computed(() => (/^\d{4}-\d{2}$/.test(route.query.month || "") ? route.query.month : today.slice(0, 7)))
const setQuery = (change) => router.replace({ query: { ...route.query, ...change } })

const upcoming = createResource({ url: "asante_one.api.life.get_life", params: { start: today, end: addDays(today, 182) } })
const memories = createResource({ url: "asante_one.api.life.get_memories" })
const monthDates = createResource({ url: "asante_one.api.life.get_life" })

watch(
	[view, filter],
	() => {
		if (view.value === "list" && filter.value === "memories") !memories.data && memories.fetch()
		else if (view.value === "list") !upcoming.data && upcoming.fetch()
	},
	{ immediate: true },
)
watch(
	[view, month],
	() => {
		if (view.value !== "month") return
		const weeks = monthWeeks(month.value)
		monthDates.fetch({ start: weeks[0][0], end: weeks.at(-1)[6] })
	},
	{ immediate: true },
)

const listed = computed(() => {
	const kinds = FILTERS.find((f) => f.key === filter.value).kinds
	return (upcoming.data || []).filter((item) => !kinds || kinds.includes(item.kind))
})
const grouped = computed(() => {
	const groups = []
	for (const item of listed.value) {
		const key = item.date.slice(0, 7)
		if (groups.at(-1)?.month !== key) groups.push({ month: key, items: [] })
		groups.at(-1).items.push(item)
	}
	return groups
})

const library = loadLibrary()
const planning = computed(() => (library.data?.resources || []).filter((r) => r.category === "Culture"))

const weeks = computed(() => monthWeeks(month.value))
// A multi day event shows on every day it covers
const onDay = (day) => (monthDates.data || []).filter((item) => item.date === day || (item.until && item.date < day && day <= item.until))
const inMonth = computed(() => (monthDates.data || []).filter((item) => item.date.slice(0, 7) === month.value))
</script>

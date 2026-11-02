<template>
	<section class="mb-[22px] mt-1.5 grid grid-cols-[auto_minmax(0,1fr)] items-center gap-3.5 nav:mb-[30px] nav:grid-cols-[auto_minmax(0,1fr)_auto] nav:gap-[22px]">
		<Avatar :name="boot.user.full_name" :image="boot.user.image" :size="phone ? 56 : 76" ring />
		<div class="min-w-0">
			<div class="flex flex-wrap items-center gap-2.5 text-sm text-grey">
				<span>{{ longDate(now) }}</span>
				<span class="font-semibold tabular-nums text-ink" aria-label="Current time in South Africa">{{ clock(now) }}</span>
				<span v-if="todayHoliday" :class="['inline-flex items-center gap-1 rounded-md px-[7px] text-[11.5px] font-semibold', KINDS.public_holiday]">
					<Icon name="flag" class="h-3 w-3" /> {{ todayHoliday.title }}
				</span>
			</div>
			<h1 class="my-1.5 text-[26px] nav:text-[clamp(28px,3.4vw,42px)]">{{ greeting(now) }}, {{ boot.user.first_name }}.</h1>
			<p v-if="roleLine" class="text-[15.5px] text-ink-2">{{ roleLine }}</p>
			<div class="beadrule mt-3.5" aria-hidden="true" />
		</div>
		<div v-if="nextDayOff" class="col-span-2 flex flex-wrap gap-2 nav:col-span-1 nav:flex-col nav:items-end">
			<RouterLink
				to="/life"
				class="flex items-center gap-2.5 rounded-xl border border-line bg-surface px-3 py-2 text-[13.5px] no-underline hover:border-line-2"
			>
				<Icon name="flag" class="h-4 w-4 text-accent" />
				<span>Next day off <b>{{ shortDay(nextDayOff.date) }}</b></span>
			</RouterLink>
		</div>
	</section>

	<button
		v-if="banner"
		class="-mt-2 mb-[26px] flex w-full flex-wrap items-center gap-3 rounded-[14px] border border-lav-2 bg-lav px-4 py-[11px] text-left hover:border-accent nav:flex-nowrap"
		@click="showAll"
	>
		<span :class="['rounded-full px-[9px] py-0.5 text-[11.5px] font-semibold', banner.urgent ? 'bg-risk-bg text-risk' : 'bg-surface text-accent']">
			{{ banner.urgent ? "Action needed" : "Announcement" }}
		</span>
		<b class="min-w-0 flex-1 text-[14.5px]">{{ banner.title }}</b>
		<span v-if="announcements.length > 1" class="hint">{{ announcements.length }} announcements</span>
		<Icon name="arrow" class="h-4 w-4 text-accent" />
	</button>

	<div class="grid grid-cols-1 items-start gap-7 nav:grid-cols-[minmax(0,1.15fr)_minmax(0,1fr)]">
		<section aria-labelledby="quick-actions">
			<div class="mb-3.5 flex items-baseline justify-between gap-3">
				<h2 id="quick-actions" class="text-[19px]">Quick actions</h2>
				<RouterLink to="/how-we-work/tools" class="link">All tools</RouterLink>
			</div>
			<div class="grid grid-cols-2 gap-2">
				<QuickAction v-for="action in boot.quick_actions" :key="action.label" :action="action" />
			</div>
			<template v-if="pinned.length">
				<h3 class="mb-2 mt-5 text-sm text-grey">Pinned</h3>
				<div class="flex flex-wrap gap-1.5">
					<a v-for="t in pinned" :key="t.tool_name" :href="t.url" target="_blank" rel="noopener" class="chip inline-flex items-center gap-1.5 no-underline">
						<Icon name="pin" class="h-3.5 w-3.5 text-accent" /> {{ t.tool_name }}
					</a>
				</div>
			</template>
		</section>

		<section class="panel" aria-labelledby="coming-up">
			<div class="mb-3.5 flex flex-wrap items-start justify-between gap-2.5">
				<div>
					<h2 id="coming-up" class="text-lg">Coming up at Asante Solutions</h2>
					<div class="text-[13px] font-medium text-grey">Holidays, closures, company events and birthdays</div>
				</div>
				<RouterLink to="/life" class="link">Life at Asante Solutions</RouterLink>
			</div>

			<Skeleton v-if="home.loading && !home.data" />
			<p v-else-if="home.error" class="hint">Coming up could not load. Refresh the page to try again.</p>
			<p v-else-if="!comingUp.length" class="hint">Nothing in the next three months.</p>
			<div v-else class="flex flex-col">
				<DateRow v-for="item in comingUp" :key="`${item.date}-${item.title}`" :item="{ ...item, to: item.to || '/life' }" />
			</div>
		</section>
	</div>

	<DeptSection v-if="home.data?.department" :department="home.data.department" />

	<section v-if="recentPolicies.length" class="mt-[34px]" aria-labelledby="recently-updated">
		<h2 id="recently-updated" class="mb-3.5 text-[19px]">Recently updated</h2>
		<div class="flex flex-col">
			<RouterLink
				v-for="policy in recentPolicies"
				:key="policy.name"
				:to="`/policies/${policy.name}`"
				class="group flex items-center gap-3.5 border-t border-line px-1 py-3 no-underline first:border-t-0"
			>
				<span class="grid h-9 w-9 flex-none place-items-center rounded-[11px] bg-sunk text-accent">
					<Icon name="book" class="h-[18px] w-[18px]" />
				</span>
				<span class="min-w-0 flex-1">
					<span class="block font-semibold group-hover:text-accent">{{ policy.title }}</span>
					<span class="block truncate text-[13px] text-grey">{{ policy.status }}, updated {{ formatDate(policy.updated_on) }}</span>
				</span>
			</RouterLink>
		</div>
	</section>

	<Announcements :open="sheetOpen" :items="sheetItems" @close="closeSheet" />
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue"
import { call, createResource } from "frappe-ui"
import { boot } from "@/boot"
import { KINDS, loadLibrary } from "@/data"
import { clock, formatDate, greeting, longDate, shortDay, todayISO } from "@/utils/dates"
import Announcements from "@/components/Announcements.vue"
import Avatar from "@/components/Avatar.vue"
import DateRow from "@/components/DateRow.vue"
import DeptSection from "@/components/DeptSection.vue"
import Icon from "@/components/Icon.vue"
import QuickAction from "@/components/QuickAction.vue"
import Skeleton from "@/components/Skeleton.vue"

const home = createResource({ url: "asante_one.api.home.get_home", auto: true })

const announcements = computed(() => home.data?.announcements || [])
const banner = computed(() => announcements.value[0])
const comingUp = computed(() => home.data?.coming_up || [])
const recentPolicies = computed(() => home.data?.recent_policies || [])

// Tools the person pinned in How we work. The library loads only when something is pinned.
const library = boot.pins.length ? loadLibrary() : null
const pinned = computed(() =>
	(library?.data?.tools || []).filter((t) => t.url && boot.pins.includes(`tool:${t.tool_name}`)),
)

const roleLine = computed(() => {
	const e = boot.employee
	return e ? [e.designation, e.department_name, e.branch].filter(Boolean).join("  |  ") : ""
})

const todayHoliday = computed(() => comingUp.value.find((i) => i.kind === "public_holiday" && i.date === todayISO(now.value)))
const nextDayOff = computed(() =>
	comingUp.value.find((i) => ["public_holiday", "closure"].includes(i.kind) && i.date > todayISO(now.value)),
)

// Announcements pop up once: unseen ones open by themselves, then are marked seen on the server
const sheetOpen = ref(false)
const sheetItems = ref([])
const unseen = computed(() => announcements.value.filter((a) => !a.seen))

let popped = false
watch(unseen, (items) => {
	if (popped || !home.data) return
	popped = true
	if (items.length) {
		sheetItems.value = items
		sheetOpen.value = true
	}
})

function showAll() {
	sheetItems.value = announcements.value
	sheetOpen.value = true
}

function closeSheet() {
	sheetOpen.value = false
	const names = sheetItems.value.filter((a) => !a.seen).map((a) => a.name)
	if (!names.length) return
	sheetItems.value.forEach((a) => (a.seen = true))
	call("asante_one.api.home.mark_announcements_seen", { names })
}

// The clock and the phone layout
const now = ref(new Date())
const phoneQuery = window.matchMedia("(max-width: 860px)")
const phone = ref(phoneQuery.matches)
const onPhoneChange = (e) => (phone.value = e.matches)
let timer
onMounted(() => {
	timer = setInterval(() => (now.value = new Date()), 30_000)
	phoneQuery.addEventListener("change", onPhoneChange)
})
onBeforeUnmount(() => {
	clearInterval(timer)
	phoneQuery.removeEventListener("change", onPhoneChange)
})
</script>

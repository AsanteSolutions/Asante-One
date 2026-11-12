<template>
	<section class="mt-[34px] rounded-[20px] border border-line bg-surface px-4 py-5 nav:px-[22px]" aria-labelledby="your-team">
		<div class="mb-4 flex flex-col gap-1 nav:flex-row nav:items-end nav:justify-between">
			<div>
				<span class="text-xs font-semibold uppercase tracking-[.08em] text-grey">Your team</span>
				<h2 id="your-team" class="text-[21px]">{{ department.name }}</h2>
			</div>
			<span class="hint">Everyone in {{ department.name }} sees this section. Set up by People and Culture.</span>
		</div>

		<div v-if="department.tools.length" class="mb-6">
			<h3 class="mb-2 text-sm text-grey">Toolkit</h3>
			<div class="grid grid-cols-1 gap-1.5 sm:grid-cols-2 wide:grid-cols-3">
				<a
					v-for="t in department.tools"
					:key="t.label"
					:href="t.url"
					target="_blank"
					rel="noopener"
					class="flex items-center gap-2.5 rounded-xl border border-line px-2.5 py-2 no-underline hover:border-lav-2"
				>
					<span class="grid h-8 w-8 flex-none place-items-center rounded-[9px] bg-lav text-accent"><Icon :name="t.icon" class="h-4 w-4" /></span>
					<span class="min-w-0 flex-1">
						<b class="block truncate text-[13.5px] font-semibold">{{ t.label }}</b>
						<small v-if="t.subtitle" class="block truncate text-[11.5px] text-grey">{{ t.subtitle }}</small>
					</span>
					<!-- Set up notes for admins; employees just see the tool -->
					<span v-if="boot.is_admin && TOOL_STATUS[t.status]" :class="['tag', TOOL_STATUS[t.status]]">{{ t.status }}</span>
				</a>
			</div>
		</div>

		<div class="grid grid-cols-1 gap-6 nav:grid-cols-[minmax(0,2fr)_minmax(0,1fr)]">
			<div>
				<h3 class="mb-2 text-sm text-grey">Reminders</h3>
				<p v-if="!department.reminders.length" class="hint">No team reminders in the next few weeks.</p>
				<div v-for="r in department.reminders" :key="`${r.date}-${r.title}`" class="flex items-center gap-3 border-t border-line py-2.5 first:border-t-0">
					<span class="w-[42px] flex-none text-center text-[11.5px] font-bold leading-[1.15] text-grey">
						<b class="block font-display text-[22px] font-semibold leading-none text-ink">{{ parts(r.date).day }}</b>
						{{ parts(r.date).month }}
					</span>
					<span class="min-w-0 flex-1">
						<span class="block text-sm font-semibold">{{ r.title }}</span>
						<span v-if="r.description" class="hint block">{{ r.description }}</span>
					</span>
					<span class="flex flex-col items-end gap-1">
						<span class="whitespace-nowrap text-xs font-semibold" :class="daysTo(r.date) <= 2 ? 'text-risk' : 'text-ok'">{{ due(r.date) }}</span>
						<span :class="['tag', REMINDER_KINDS[r.kind] || REMINDER_KINDS.Suggested]">{{ r.kind }}</span>
					</span>
				</div>
			</div>

			<div v-if="equipment.length">
				<h3 class="mb-2 text-sm text-grey">Equipment</h3>
				<div class="grid grid-cols-2 gap-1.5">
					<component
						:is="e.to ? RouterLink : 'a'"
						v-for="e in equipment"
						:key="e.label"
						v-bind="e.to ? { to: e.to } : { href: e.href, target: '_blank', rel: 'noopener' }"
						class="flex flex-col gap-1.5 rounded-xl border border-line p-2.5 text-[13px] font-semibold no-underline hover:border-lav-2"
					>
						<Icon :name="e.icon" class="h-[18px] w-[18px] text-accent" />
						{{ e.label }}
					</component>
				</div>
			</div>
		</div>
	</section>
</template>

<script setup>
import { computed } from "vue"
import { RouterLink } from "vue-router"
import { boot } from "@/boot"
import { daysBetween, parts, todayISO } from "@/utils/dates"
import Icon from "@/components/Icon.vue"

defineProps({ department: { type: Object, required: true } })

const TOOL_STATUS = {
	"Route to verify": "bg-warn-bg text-warn",
	"Confirm team uses it": "border border-dashed border-line-2 text-grey",
}
const REMINDER_KINDS = {
	"Company rhythm": "bg-ok-bg text-ok",
	"SARS rule": "bg-ok-bg text-ok",
	Suggested: "border border-dashed border-line-2 text-grey",
	Confirm: "bg-warn-bg text-warn",
}

const today = todayISO()
const daysTo = (iso) => daysBetween(today, iso)
function due(iso) {
	const days = daysTo(iso)
	return days === 0 ? "Today" : days === 1 ? "Tomorrow" : `In ${days} days`
}

// Check out and check in open ERPNext; the custodian also gets the full register
const equipment = computed(() => {
	const links = boot.links
	return [
		links.check_out && { label: "Check out kit", icon: "box", href: links.check_out },
		links.check_in && { label: "Check in kit", icon: "check", href: links.check_in },
		boot.is_custodian ? { label: "Full register", icon: "grid", to: "/equipment/register" } : { label: "Available kit", icon: "camera", to: "/equipment/kit" },
		links.incident_template && { label: "Incident report", icon: "alert", href: links.incident_template },
	].filter(Boolean)
})
</script>

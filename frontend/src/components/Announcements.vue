<template>
	<Sheet :open="open" label="Announcements" @close="close">
		<template v-if="current">
			<div class="mb-2.5 flex flex-wrap items-center gap-2">
				<span :class="tag(current)">{{ current.urgent ? "Action needed" : "Announcement" }}</span>
				<span class="hint">{{ formatDate(current.published_on) }}</span>
			</div>
			<h2 ref="heading" tabindex="-1" class="text-2xl focus:outline-none">{{ current.title }}</h2>
			<div v-if="current.body" class="mt-2.5 text-ink-2 [&_a]:text-accent [&_p]:mb-2" v-html="current.body" />
			<div v-if="rest.length" class="mt-[18px] border-t border-line pt-1.5">
				<button
					v-for="other in rest"
					:key="other.name"
					class="group flex w-full items-center gap-3 border-t border-line px-0.5 py-2.5 text-left first:border-t-0"
					@click="show(other)"
				>
					<span class="min-w-0 flex-1">
						<span class="block text-sm font-semibold group-hover:text-accent">{{ other.title }}</span>
						<span class="hint block">{{ other.urgent ? "Action needed · " : "" }}{{ formatDate(other.published_on) }}</span>
					</span>
					<Icon name="right" class="h-4 w-4 flex-none text-grey group-hover:text-accent" />
				</button>
			</div>
			<div class="mt-[18px] flex flex-wrap justify-end gap-2">
				<template v-if="current.read_more">
					<RouterLink v-if="isPage(current.read_more)" :to="current.read_more" class="btn" @click="close">Read more</RouterLink>
					<a v-else :href="current.read_more" target="_blank" rel="noopener" class="btn">Read more</a>
				</template>
				<button class="btn btn-primary" @click="close">Got it</button>
			</div>
		</template>
	</Sheet>
</template>

<script setup>
import { computed, nextTick, ref, watch } from "vue"
import { formatDate } from "@/utils/dates"
import Icon from "@/components/Icon.vue"
import Sheet from "@/components/Sheet.vue"

const props = defineProps({ open: Boolean, items: { type: Array, default: () => [] } })
const emit = defineEmits(["close"])
const heading = ref(null)

// The announcement being read. Each time the sheet opens it starts on the newest.
const selected = ref(null)
watch(
	() => props.open,
	(open) => open && (selected.value = props.items[0]?.name),
)
const current = computed(() => props.items.find((a) => a.name === selected.value) || props.items[0])
const rest = computed(() => props.items.filter((a) => a !== current.value))
const close = () => emit("close")

async function show(item) {
	selected.value = item.name
	// Back to the top of the sheet, with focus on the title for keyboard and screen reader users
	await nextTick()
	heading.value?.focus()
	heading.value?.closest("[role=dialog]")?.scrollTo({ top: 0 })
}

// ASANTE ONE pages stay in the app; Desk, Frappe HR and outside links open in a new tab
const isPage = (link) => link.startsWith("/") && !/^\/(desk|app|hrms|api|files)\b/.test(link)

const tag = (item) =>
	[
		"rounded-full px-[9px] py-0.5 text-[11.5px] font-semibold",
		item.urgent ? "bg-risk-bg text-risk" : "bg-lav text-accent",
	].join(" ")
</script>

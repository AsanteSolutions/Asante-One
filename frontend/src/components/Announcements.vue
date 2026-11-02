<template>
	<Sheet :open="open" label="Announcements" @close="close">
		<template v-if="first">
			<div class="mb-2.5 flex flex-wrap items-center gap-2">
				<span :class="tag(first)">{{ first.urgent ? "Action needed" : "Announcement" }}</span>
				<span class="hint">{{ formatDate(first.published_on) }}</span>
			</div>
			<h2 class="text-2xl">{{ first.title }}</h2>
			<div v-if="first.body" class="mt-2.5 text-ink-2 [&_a]:text-accent [&_p]:mb-2" v-html="first.body" />
			<div v-if="rest.length" class="mt-[18px] border-t border-line pt-1.5">
				<div v-for="other in rest" :key="other.name" class="border-t border-line px-0.5 py-2.5 first:border-t-0">
					<div class="text-sm font-semibold">{{ other.title }}</div>
					<div class="hint">{{ formatDate(other.published_on) }}</div>
				</div>
			</div>
			<div class="mt-[18px] flex flex-wrap justify-end gap-2">
				<template v-if="first.read_more">
					<RouterLink v-if="isPage(first.read_more)" :to="first.read_more" class="btn" @click="close">Read more</RouterLink>
					<a v-else :href="first.read_more" target="_blank" rel="noopener" class="btn">Read more</a>
				</template>
				<button class="btn btn-primary" @click="close">Got it</button>
			</div>
		</template>
	</Sheet>
</template>

<script setup>
import { computed } from "vue"
import { formatDate } from "@/utils/dates"
import Sheet from "@/components/Sheet.vue"

const props = defineProps({ open: Boolean, items: { type: Array, default: () => [] } })
const emit = defineEmits(["close"])

const first = computed(() => props.items[0])
const rest = computed(() => props.items.slice(1))
const close = () => emit("close")

// ASANTE ONE pages stay in the app; Desk, Frappe HR and outside links open in a new tab
const isPage = (link) => link.startsWith("/") && !/^\/(desk|app|hrms|api|files)\b/.test(link)

const tag = (item) =>
	[
		"rounded-full px-[9px] py-0.5 text-[11.5px] font-semibold",
		item.urgent ? "bg-risk-bg text-risk" : "bg-lav text-accent",
	].join(" ")
</script>

<template>
	<Teleport to="body">
		<div
			v-if="palette.open"
			class="fixed inset-0 z-[70] flex items-start justify-center bg-[rgba(24,14,30,.32)] nav:p-3 nav:pt-[12vh]"
			@click.self="close"
		>
			<div
				role="dialog"
				aria-modal="true"
				aria-label="Search ASANTE ONE"
				class="flex h-full w-full flex-col overflow-hidden bg-surface shadow-[0_30px_80px_rgba(24,14,30,.25)] nav:h-auto nav:max-h-[70vh] nav:max-w-[640px] nav:rounded-[20px]"
			>
				<div class="flex items-center gap-2.5 border-b border-line px-4 py-3">
					<Icon name="search" class="h-5 w-5 flex-none text-grey" />
					<input
						ref="input"
						v-model="query"
						class="min-w-0 flex-1 border-0 bg-transparent text-base text-ink placeholder:text-grey focus:outline-none"
						placeholder="Search actions, policies, folders, tools and people"
						aria-label="Search"
						role="combobox"
						aria-controls="palette-results"
						:aria-activedescendant="results.length ? `palette-${selected}` : undefined"
						aria-expanded="true"
						@keydown.down.prevent="move(1)"
						@keydown.up.prevent="move(-1)"
						@keydown.enter.prevent="pick(results[selected])"
					/>
					<button class="grid h-9 w-9 place-items-center rounded-[10px] text-grey hover:bg-sunk" aria-label="Close search" @click="close">
						<Icon name="close" class="h-[18px] w-[18px]" />
					</button>
				</div>

				<div id="palette-results" class="flex-1 overflow-auto p-2" role="listbox" aria-label="Results">
					<div v-if="!query" class="flex flex-wrap gap-1.5 px-2 pb-2 pt-1">
						<button v-for="s in SUGGESTIONS" :key="s" class="chip" @click="query = s">{{ s }}</button>
					</div>
					<template v-for="(item, n) in results" :key="`${item.group}-${item.title}-${n}`">
						<div v-if="n === 0 || results[n - 1].group !== item.group" class="px-2.5 pb-1 pt-3 text-xs font-semibold text-grey">{{ item.group }}</div>
						<button
							:id="`palette-${n}`"
							role="option"
							:aria-selected="n === selected"
							class="flex w-full items-center gap-3 rounded-[11px] px-2.5 py-2 text-left"
							:class="n === selected ? 'bg-lav' : 'hover:bg-sunk'"
							@mousemove="selected = n"
							@click="pick(item)"
						>
							<span class="grid h-8 w-8 flex-none place-items-center rounded-[9px] bg-sunk text-accent"><Icon :name="ICONS[item.group] || 'link'" class="h-4 w-4" /></span>
							<span class="min-w-0 flex-1">
								<span class="block truncate text-sm font-semibold">{{ item.title }}</span>
								<span v-if="item.subtitle" class="block truncate text-[12.5px] text-grey">{{ item.subtitle }}</span>
							</span>
							<span v-if="item.restricted" class="tag bg-risk-bg text-risk">Restricted</span>
							<Icon v-if="item.kind !== 'page'" name="ext" class="h-3.5 w-3.5 flex-none text-grey" />
						</button>
					</template>
					<p v-if="query && !results.length" class="px-3 py-6 text-center text-sm text-ink-2">
						Nothing matches "{{ query }}". Try a shorter word, or ask
						<button class="link" @click="pick({ kind: 'page', to: '/how-we-work/who-to-ask' })">who to ask</button>.
					</p>
				</div>
				<p class="hint m-0 hidden border-t border-line px-4 py-2 nav:block">Up and down to move, Enter to open, Esc to close. Searches titles and descriptions, not inside Drive documents.</p>
			</div>
		</div>
	</Teleport>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue"
import { useRouter } from "vue-router"
import { boot } from "@/boot"
import { NAV } from "@/nav"
import { resolveAction } from "@/utils/actions"
import { palette } from "@/utils/palette"
import Icon from "@/components/Icon.vue"

const SUGGESTIONS = ["Leave", "Work from home", "Payslip", "Expense", "Onboarding", "Templates"]
const ICONS = {
	Pages: "apps",
	"Frappe HR": "people",
	Policies: "book",
	Resources: "folder",
	Tools: "grid",
	"Who to ask": "user",
}

// Pages are searchable too, including each tab of How we work and the Life views
const PAGES = [
	...NAV.filter((n) => n.to !== "/").map((n) => ({ title: n.label, to: n.to })),
	{ title: "SOPs and templates", subtitle: "How we work", to: "/how-we-work/sops" },
	{ title: "Tools we use", subtitle: "How we work", to: "/how-we-work/tools" },
	{ title: "Who to ask", subtitle: "How we work", to: "/how-we-work/who-to-ask" },
	{ title: "Request desk", subtitle: "How we work", to: "/how-we-work/request-desk" },
	{ title: "Company calendar", subtitle: "Life at Asante Solutions, month view", to: "/life?view=month" },
	{ title: "Public holidays and closures", subtitle: "Life at Asante Solutions", to: "/life?show=days-off" },
	{ title: "Birthdays and anniversaries", subtitle: "Life at Asante Solutions", to: "/life?show=celebrations" },
	{ title: "Memories", subtitle: "Past company events", to: "/life?show=memories" },
].map((p) => ({ ...p, group: "Pages", kind: "page" }))

const router = useRouter()
const query = ref("")
const selected = ref(0)
const input = ref(null)

const index = computed(() => [...PAGES, ...boot.search])
const results = computed(() => {
	const words = query.value.trim().toLowerCase().split(/\s+/).filter(Boolean)
	if (!words.length) return index.value.filter((item) => item.group === "Frappe HR").slice(0, 7)
	return index.value
		.filter((item) => {
			const text = `${item.title} ${item.subtitle || ""} ${item.group}`.toLowerCase()
			return words.every((word) => text.includes(word))
		})
		.slice(0, 40)
})

watch(results, () => (selected.value = 0))
watch(
	() => palette.open,
	async (open) => {
		if (!open) return
		query.value = ""
		await nextTick()
		input.value?.focus()
	},
)

function move(by) {
	if (!results.value.length) return
	selected.value = (selected.value + by + results.value.length) % results.value.length
	nextTick(() => document.getElementById(`palette-${selected.value}`)?.scrollIntoView({ block: "nearest" }))
}

function close() {
	palette.open = false
}

function pick(item) {
	if (!item) return
	const target = resolveAction(item)
	close()
	if (target?.to) router.push(target.to)
	else if (target?.href) window.open(target.href, "_blank", "noopener")
}

// "/" or Ctrl K opens search from anywhere, unless the person is typing in a field
function onKey(event) {
	const typing = ["INPUT", "TEXTAREA", "SELECT"].includes(event.target.tagName) || event.target.isContentEditable
	if (event.key === "Escape" && palette.open) close()
	else if ((event.key === "k" && (event.ctrlKey || event.metaKey)) || (event.key === "/" && !typing)) {
		event.preventDefault()
		palette.open = true
	}
}
onMounted(() => document.addEventListener("keydown", onKey))
onBeforeUnmount(() => document.removeEventListener("keydown", onKey))
</script>

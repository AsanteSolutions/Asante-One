<template>
	<Teleport to="body">
		<Transition
			enter-from-class="opacity-0"
			enter-active-class="transition-opacity duration-150"
			leave-to-class="opacity-0"
			leave-active-class="transition-opacity duration-100"
		>
			<div v-if="open" class="fixed inset-0 z-[60] flex items-center justify-center bg-[rgba(24,14,30,.32)] p-3" @click.self="close">
				<div
					ref="panel"
					role="dialog"
					aria-modal="true"
					:aria-label="label"
					class="max-h-[calc(100%-40px)] w-full max-w-[560px] overflow-auto rounded-[22px] bg-surface p-[26px] shadow-[0_30px_80px_rgba(24,14,30,.25)] focus:outline-none"
					tabindex="-1"
				>
					<slot />
				</div>
			</div>
		</Transition>
	</Teleport>
</template>

<script setup>
import { nextTick, onBeforeUnmount, ref, watch } from "vue"

const props = defineProps({ open: Boolean, label: { type: String, default: "" } })
const emit = defineEmits(["close"])
const panel = ref(null)

const close = () => emit("close")
const onKey = (event) => event.key === "Escape" && close()

watch(
	() => props.open,
	async (open) => {
		if (open) {
			document.addEventListener("keydown", onKey)
			await nextTick()
			panel.value?.focus()
		} else {
			document.removeEventListener("keydown", onKey)
		}
	},
	{ immediate: true },
)
onBeforeUnmount(() => document.removeEventListener("keydown", onKey))
</script>

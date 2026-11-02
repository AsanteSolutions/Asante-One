<template>
	<span
		class="relative grid flex-none place-items-center overflow-hidden rounded-full font-semibold text-white"
		:class="[image ? '' : colour, ring ? 'shadow-[0_0_0_3px_var(--canvas),0_0_0_5px_var(--lav-2)]' : '']"
		:style="{ width: `${size}px`, height: `${size}px`, fontSize: `${size * 0.36}px` }"
	>
		<img v-if="image && !failed" :src="image" :alt="name" class="block h-full w-full object-cover" @error="failed = true" />
		<span v-else aria-hidden="true">{{ initials }}</span>
	</span>
</template>

<script setup>
import { computed, ref } from "vue"

const props = defineProps({
	name: { type: String, default: "" },
	image: { type: String, default: null },
	size: { type: Number, default: 36 },
	ring: { type: Boolean, default: false },
})

const failed = ref(false)

const initials = computed(() =>
	props.name
		.split(/\s+/)
		.filter(Boolean)
		.map((word) => word[0])
		.slice(0, 2)
		.join("")
		.toUpperCase(),
)

// The prototype's five avatar colours, picked from the name so a person keeps theirs
const COLOURS = ["bg-[#6B4E8F]", "bg-[#2F6D6A]", "bg-[#8A5A2B]", "bg-[#3D5A8A]", "bg-[#7A3E5A]"]
const colour = computed(() => {
	let hash = 0
	for (const char of props.name) hash = (hash * 31 + char.charCodeAt(0)) >>> 0
	return COLOURS[hash % COLOURS.length]
})
</script>

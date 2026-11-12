<template>
	<div class="mb-3.5 flex flex-col gap-3">
		<input v-model="query" class="input nav:max-w-[260px]" :placeholder="placeholder" :aria-label="placeholder" />
		<div class="-mx-4 flex gap-1.5 overflow-x-auto px-4 nav:mx-0 nav:flex-wrap nav:px-0" role="group" aria-label="Kind of kit">
			<button v-for="name in groups" :key="name" :class="['chip', group === name && 'chip-on']" :aria-pressed="group === name" @click="group = name">
				{{ name }}
			</button>
		</div>
	</div>
</template>

<script setup>
// The search box and item group chips shared by Available kit and the full register
defineProps({ groups: { type: Array, required: true }, placeholder: { type: String, required: true } })
const query = defineModel("query", { type: String })
const group = defineModel("group", { type: String })
</script>

<template>
	<div class="max-w-[560px] rounded-[14px] border-[1.5px] border-dashed border-line-2 bg-canvas p-5 text-sm text-ink-2">
		<b v-if="title" class="mb-1 block text-ink">{{ title }}</b>
		<slot />
	</div>
</template>

<script setup>
defineProps({ title: { type: String, default: null } })
</script>

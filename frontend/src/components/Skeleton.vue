<template>
	<div class="flex flex-col gap-3" aria-busy="true" aria-label="Loading">
		<div v-for="n in rows" :key="n" class="h-10 animate-pulse rounded-lg bg-sunk" />
	</div>
</template>

<script setup>
defineProps({ rows: { type: Number, default: 4 } })
</script>

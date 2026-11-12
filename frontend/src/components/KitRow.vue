<template>
	<div class="flex items-center gap-3 border-t border-line py-2.5 first:border-t-0">
		<span class="min-w-0 flex-1">
			<span class="block text-sm font-semibold">
				{{ item.item_name }}<span v-if="qty !== null && qty !== 1" class="text-grey"> ×{{ count(qty) }}</span>
			</span>
			<span v-if="$slots.default" class="hint block"><slot /></span>
		</span>
		<span v-if="$slots.right" class="flex flex-none flex-col items-end gap-1"><slot name="right" /></span>
	</div>
</template>

<script setup>
import { count } from "@/utils/equipment"

// One line of shoot kit: the item, how many when more than one, a subtitle, and tags on the right
defineProps({ item: { type: Object, required: true }, qty: { type: Number, default: null } })
</script>

<template>
	<component
		:is="item.to ? RouterLink : 'div'"
		v-bind="item.to ? { to: item.to } : {}"
		class="group flex items-center gap-3 border-t border-line py-[9px] text-left no-underline first:border-t-0"
	>
		<span class="w-[42px] flex-none text-center text-[11.5px] font-bold leading-[1.15] text-grey">
			<b class="block font-display text-[22px] font-semibold leading-none tracking-[-.02em] text-ink">{{ parts(item.date).day }}</b>
			{{ parts(item.date).month }}
		</span>
		<Avatar v-if="item.person" :name="item.person.name" :image="item.person.image" :size="34" />
		<span class="min-w-0 flex-1">
			<span class="block text-sm font-semibold" :class="{ 'group-hover:text-accent': item.to }">{{ item.title }}</span>
			<span v-if="item.subtitle" class="hint block">{{ item.subtitle }}</span>
		</span>
		<span :class="['tag', KINDS[item.kind]]">{{ item.label }}</span>
	</component>
</template>

<script setup>
import { RouterLink } from "vue-router"
import { KINDS } from "@/data"
import { parts } from "@/utils/dates"
import Avatar from "@/components/Avatar.vue"

// One date in Coming up or Life: a holiday, a company event, a birthday or an anniversary
defineProps({ item: { type: Object, required: true } })
</script>

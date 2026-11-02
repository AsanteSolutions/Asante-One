<template>
	<component
		:is="to ? RouterLink : href ? 'a' : 'div'"
		v-bind="to ? { to } : href ? { href, target: '_blank', rel: 'noopener' } : {}"
		class="group flex items-center gap-3.5 border-t border-line px-1 py-3 text-left no-underline first:border-t-0"
	>
		<span class="grid h-9 w-9 flex-none place-items-center rounded-[11px] bg-sunk text-accent">
			<Icon :name="icon" class="h-[18px] w-[18px]" />
		</span>
		<span class="min-w-0 flex-1">
			<span class="block font-semibold" :class="{ 'group-hover:text-accent': to || href }">{{ title }}</span>
			<span v-if="subtitle" class="block text-[13px] text-grey">{{ subtitle }}</span>
		</span>
		<slot />
		<Icon v-if="href" name="ext" class="h-3.5 w-3.5 flex-none text-grey" />
	</component>
</template>

<script setup>
import { RouterLink } from "vue-router"
import Icon from "@/components/Icon.vue"

// A list row that goes somewhere: a page in ASANTE ONE (to) or an outside link (href), which opens in a new tab
defineProps({
	to: { type: String, default: null },
	href: { type: String, default: null },
	icon: { type: String, default: "link" },
	title: { type: String, required: true },
	subtitle: { type: String, default: null },
})
</script>

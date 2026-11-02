<template>
	<component
		:is="target?.to ? RouterLink : 'a'"
		v-if="target"
		v-bind="target.to ? { to: target.to } : { href: target.href, target: '_blank', rel: 'noopener' }"
		class="flex min-h-[60px] items-center gap-[11px] rounded-[14px] border border-line bg-surface px-3 py-2.5 text-left no-underline transition-[border-color,box-shadow] duration-100 hover:border-lav-2 hover:shadow"
	>
		<span class="grid h-8 w-8 flex-none place-items-center rounded-[9px] bg-lav text-accent">
			<Icon :name="action.icon" class="h-[17px] w-[17px]" />
		</span>
		<span class="min-w-0">
			<b class="block text-[13.5px] font-semibold leading-tight">{{ action.label }}</b>
			<small v-if="action.subtitle" class="mt-px block text-[11.5px] text-grey">{{ action.subtitle }}</small>
		</span>
	</component>
</template>

<script setup>
import { computed } from "vue"
import { RouterLink } from "vue-router"
import { resolveAction } from "@/utils/actions"
import Icon from "@/components/Icon.vue"

const props = defineProps({ action: { type: Object, required: true } })
const target = computed(() => resolveAction(props.action))
</script>

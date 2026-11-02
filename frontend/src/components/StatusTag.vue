<template>
	<span v-if="tag" :class="['tag', tag.class]">{{ tag.label }}</span>
</template>

<script setup>
import { computed } from "vue"
import { STATUS } from "@/data"

const props = defineProps({ status: { type: String, default: null } })
const tag = computed(() => STATUS[props.status])
</script>

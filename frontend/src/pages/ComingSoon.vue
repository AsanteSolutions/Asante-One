<template>
	<div class="mb-[26px] mt-1">
		<h1 class="text-[clamp(28px,3vw,38px)]">{{ route.meta.title }}</h1>
	</div>

	<!-- On phones, More lists the pages the tab bar has no room for -->
	<nav v-if="route.path === '/more'" class="flex flex-col" aria-label="More pages">
		<RouterLink
			v-for="item in more"
			:key="item.label"
			:to="item.to"
			class="flex items-center gap-3.5 border-t border-line px-1 py-3 font-semibold no-underline first:border-t-0"
		>
			<span class="grid h-9 w-9 place-items-center rounded-[11px] bg-sunk text-accent"><Icon :name="item.icon" class="h-[18px] w-[18px]" /></span>
			{{ item.label }}
		</RouterLink>
		<a
			v-if="boot.is_admin"
			:href="MANAGE_CONTENT.href"
			class="flex items-center gap-3.5 border-t border-line px-1 py-3 font-semibold no-underline"
		>
			<span class="grid h-9 w-9 place-items-center rounded-[11px] bg-sunk text-accent"><Icon :name="MANAGE_CONTENT.icon" class="h-[18px] w-[18px]" /></span>
			{{ MANAGE_CONTENT.label }}
		</a>
	</nav>

	<div v-else class="max-w-[560px] rounded-[14px] border-[1.5px] border-dashed border-line-2 bg-canvas p-5 text-sm text-ink-2">
		<b class="mb-1 block text-ink">This page is being built</b>
		It arrives in the next build.
	</div>
</template>

<script setup>
import { computed } from "vue"
import { useRoute } from "vue-router"
import { boot } from "@/boot"
import { MANAGE_CONTENT, NAV, TABS } from "@/nav"
import Icon from "@/components/Icon.vue"

const route = useRoute()
const more = computed(() => NAV.filter((item) => !TABS.some((tab) => tab.to === item.to)))
</script>

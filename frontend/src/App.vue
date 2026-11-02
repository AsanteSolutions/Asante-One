<template>
	<div class="grid min-h-full grid-cols-1 nav:grid-cols-[232px_minmax(0,1fr)]">
		<aside
			class="sticky top-0 hidden h-screen flex-col overflow-auto border-r border-line bg-surface px-3 py-[18px] nav:flex"
			aria-label="Main navigation"
		>
			<RouterLink to="/" class="flex items-center gap-[11px] px-2.5 pb-5 pt-1 no-underline">
				<BrandMark />
				<span>
					<b class="block font-display text-[15px] font-bold tracking-[.06em]">ASANTE ONE</b>
					<span class="text-xs text-grey">Asante Solutions</span>
				</span>
			</RouterLink>
			<nav class="flex flex-col gap-px">
				<RouterLink
					v-for="item in NAV"
					:key="item.to"
					:to="item.to"
					class="relative flex items-center gap-[11px] rounded-[10px] px-2.5 py-[9px] text-[14.5px] font-medium no-underline"
					:class="
						isActive(route, item.to)
							? 'bg-lav font-semibold text-accent before:absolute before:-left-3 before:bottom-2 before:top-2 before:w-[3px] before:rounded-r-[3px] before:bg-accent-bg'
							: 'text-ink-2 hover:bg-sunk hover:text-ink'
					"
					:aria-current="isActive(route, item.to) ? 'page' : undefined"
				>
					<Icon :name="item.icon" class="h-[18px] w-[18px] flex-none" />
					<span>{{ item.label }}</span>
				</RouterLink>
				<template v-if="boot.is_admin">
					<div class="px-2.5 pb-1.5 pt-[18px] text-xs font-semibold text-grey">For admins</div>
					<a
						:href="MANAGE_CONTENT.href"
						class="flex items-center gap-[11px] rounded-[10px] px-2.5 py-[9px] text-[14.5px] font-medium text-ink-2 no-underline hover:bg-sunk hover:text-ink"
					>
						<Icon :name="MANAGE_CONTENT.icon" class="h-[18px] w-[18px] flex-none" />
						<span>{{ MANAGE_CONTENT.label }}</span>
					</a>
				</template>
			</nav>
		</aside>

		<main class="min-w-0">
			<TopBar />
			<div class="mx-auto max-w-[1320px] px-4 pb-[104px] pt-3.5 nav:px-8 nav:pb-14 nav:pt-7">
				<RouterView />
			</div>
		</main>
	</div>

	<nav
		class="fixed inset-x-0 bottom-0 z-40 grid grid-cols-5 border-t border-line bg-surface px-1.5 pb-[calc(6px+env(safe-area-inset-bottom,0px))] pt-1.5 nav:hidden"
		aria-label="Mobile navigation"
	>
		<RouterLink
			v-for="tab in TABS"
			:key="tab.to"
			:to="tab.to"
			class="flex flex-col items-center gap-0.5 rounded-[10px] py-1.5 text-[11px] font-semibold no-underline"
			:class="isActive(route, tab.to) ? 'text-accent' : 'text-grey'"
		>
			<Icon :name="tab.icon" class="h-[21px] w-[21px]" />
			<span>{{ tab.label }}</span>
		</RouterLink>
	</nav>

	<CommandPalette />
</template>

<script setup>
import { useRoute } from "vue-router"
import { boot } from "@/boot"
import { MANAGE_CONTENT, NAV, TABS, isActive } from "@/nav"
import BrandMark from "@/components/BrandMark.vue"
import CommandPalette from "@/components/CommandPalette.vue"
import Icon from "@/components/Icon.vue"
import TopBar from "@/components/TopBar.vue"

const route = useRoute()
</script>

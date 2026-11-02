<template>
	<div
		class="sticky top-0 z-20 flex items-center gap-3 border-b px-3.5 py-2.5 backdrop-blur-md nav:px-8 nav:py-3"
		:class="scrolled ? 'border-line' : 'border-transparent'"
		style="background: color-mix(in srgb, var(--canvas) 86%, transparent)"
	>
		<RouterLink to="/" class="flex items-center gap-2.5 no-underline nav:hidden" aria-label="ASANTE ONE home">
			<BrandMark />
		</RouterLink>
		<div class="hidden min-w-0 flex-1 items-center gap-1.5 truncate text-[13px] text-grey nav:flex">
			<template v-if="route.meta.title !== 'Home'">
				<RouterLink to="/" class="no-underline hover:text-ink">Home</RouterLink>
				<span>/</span>
			</template>
			<span class="font-semibold text-ink">{{ route.meta.title }}</span>
		</div>
		<div class="flex-1 nav:hidden" />

		<button
			class="grid h-10 w-10 place-items-center rounded-xl text-ink-2 hover:bg-sunk"
			:aria-label="isDark ? 'Switch to light' : 'Switch to dark'"
			@click="toggleTheme"
		>
			<Icon :name="isDark ? 'sun' : 'moon'" class="h-[19px] w-[19px]" />
		</button>

		<div ref="menuRoot" class="relative">
			<button
				class="flex items-center gap-2.5 rounded-[14px] p-1 text-left hover:bg-sunk wide:pr-2.5"
				aria-haspopup="menu"
				:aria-expanded="menuOpen"
				aria-label="Your profile menu"
				@click="menuOpen = !menuOpen"
			>
				<Avatar :name="boot.user.full_name" :image="boot.user.image" />
				<span class="hidden wide:block">
					<span class="block text-sm font-semibold leading-tight">{{ boot.user.full_name }}</span>
					<span v-if="boot.employee" class="block text-xs leading-tight text-grey">{{ boot.employee.designation }}</span>
				</span>
			</button>

			<div
				v-if="menuOpen"
				role="menu"
				class="absolute right-0 top-[calc(100%+8px)] z-[62] w-[min(320px,calc(100vw-24px))] rounded-[18px] border border-line bg-surface p-2.5 shadow"
			>
				<div class="mb-1.5 flex items-center gap-3 border-b border-line px-2.5 pb-3.5 pt-2.5">
					<Avatar :name="boot.user.full_name" :image="boot.user.image" :size="48" />
					<div class="min-w-0">
						<div class="font-semibold">{{ boot.user.full_name }}</div>
						<div v-if="boot.employee" class="truncate text-[13px] text-grey">{{ boot.employee.designation }}</div>
						<div v-if="boot.employee" class="truncate text-[13px] text-grey">
							{{ [boot.employee.department_name, boot.employee.branch].filter(Boolean).join(" · ") }}
						</div>
					</div>
				</div>
				<a v-if="profileHref" :href="profileHref" target="_blank" rel="noopener" role="menuitem" :class="item">
					<Icon name="user" class="h-[17px] w-[17px] text-grey" /> My employee profile
				</a>
				<a :href="`/desk/user/${encodeURIComponent(boot.user.name)}`" target="_blank" rel="noopener" role="menuitem" :class="item">
					<Icon name="star" class="h-[17px] w-[17px] text-grey" /> Change my photo
				</a>
				<a href="/desk" role="menuitem" :class="item">
					<Icon name="apps" class="h-[17px] w-[17px] text-grey" /> Open AsantePower desk
				</a>
				<a href="/api/method/web_logout" role="menuitem" :class="item">
					<Icon name="logout" class="h-[17px] w-[17px] text-grey" /> Sign out
				</a>
			</div>
		</div>
	</div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue"
import { useRoute } from "vue-router"
import { boot, hrAction } from "@/boot"
import { hrHref } from "@/utils/actions"
import { isDark, toggleTheme } from "@/utils/theme"
import Avatar from "@/components/Avatar.vue"
import BrandMark from "@/components/BrandMark.vue"
import Icon from "@/components/Icon.vue"

const route = useRoute()
const scrolled = ref(false)
const menuOpen = ref(false)
const menuRoot = ref(null)
const item = "flex w-full items-center gap-3 rounded-[10px] p-2.5 text-left text-sm no-underline hover:bg-sunk"

const profileHref = computed(() => {
	const action = hrAction("profile")
	return action && hrHref(action)
})

const onScroll = () => (scrolled.value = window.scrollY > 4)
const onClick = (event) => {
	if (menuOpen.value && !menuRoot.value?.contains(event.target)) menuOpen.value = false
}
const onKey = (event) => event.key === "Escape" && (menuOpen.value = false)

watch(() => route.fullPath, () => (menuOpen.value = false))
onMounted(() => {
	window.addEventListener("scroll", onScroll, { passive: true })
	document.addEventListener("click", onClick)
	document.addEventListener("keydown", onKey)
})
onBeforeUnmount(() => {
	window.removeEventListener("scroll", onScroll)
	document.removeEventListener("click", onClick)
	document.removeEventListener("keydown", onKey)
})
</script>

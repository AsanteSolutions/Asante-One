import { createRouter, createWebHistory } from "vue-router"

const later = (title) => ({ component: () => import("@/pages/ComingSoon.vue"), meta: { title } })
const page = (component, title) => ({ component, meta: { title } })

const routes = [
	{ path: "/", name: "home", ...page(() => import("@/pages/Home.vue"), "Home") },
	{ path: "/hr", ...page(() => import("@/pages/HR.vue"), "People and HR") },
	{ path: "/policies", ...page(() => import("@/pages/Policies.vue"), "Policies") },
	{ path: "/policies/:name", props: true, ...page(() => import("@/pages/Policy.vue"), "Policies") },
	{ path: "/life", ...page(() => import("@/pages/Life.vue"), "Life at Asante Solutions") },
	{ path: "/life/:name", props: true, ...page(() => import("@/pages/LifeEvent.vue"), "Life at Asante Solutions") },
	{ path: "/how-we-work/:tab?", props: true, ...page(() => import("@/pages/HowWeWork.vue"), "How we work") },
	{ path: "/equipment/:tab?", ...later("Equipment") },
	{ path: "/more", ...later("More") },
	{ path: "/:path(.*)*", component: () => import("@/pages/NotFound.vue"), meta: { title: "Not found" } },
]

const router = createRouter({
	history: createWebHistory("/one"),
	routes,
	// Changing a filter in the address keeps the scroll position; a new page starts at the top
	scrollBehavior: (to, from, saved) => saved || (to.path === from.path ? undefined : { top: 0 }),
})

router.afterEach((to) => {
	document.title = to.meta.title === "Home" ? "ASANTE ONE" : `${to.meta.title} · ASANTE ONE`
})

export default router

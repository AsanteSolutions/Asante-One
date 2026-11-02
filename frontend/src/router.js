import { createRouter, createWebHistory } from "vue-router"

const later = (title) => ({ component: () => import("@/pages/ComingSoon.vue"), meta: { title } })

const routes = [
	{ path: "/", name: "home", component: () => import("@/pages/Home.vue"), meta: { title: "Home" } },
	{ path: "/hr", ...later("People and HR") },
	{ path: "/policies/:name?", ...later("Policies") },
	{ path: "/life/:event?", ...later("Life at Asante Solutions") },
	{ path: "/how-we-work/:tab?", ...later("How we work") },
	{ path: "/equipment/:tab?", ...later("Equipment") },
	{ path: "/more", ...later("More") },
	{ path: "/:path(.*)*", component: () => import("@/pages/NotFound.vue"), meta: { title: "Not found" } },
]

const router = createRouter({
	history: createWebHistory("/one"),
	routes,
	scrollBehavior: () => ({ top: 0 }),
})

router.afterEach((to) => {
	document.title = to.meta.title === "Home" ? "ASANTE ONE" : `${to.meta.title} · ASANTE ONE`
})

export default router

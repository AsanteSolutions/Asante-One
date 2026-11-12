import "./index.css"
import { createApp } from "vue"
import { frappeRequest, setConfig } from "frappe-ui"
import App from "./App.vue"
import router from "./router"
import { loadBoot } from "./boot"

setConfig("resourceFetcher", frappeRequest)

// frappe-ui rethrows a failed request after recording it on the resource. Every page shows its own
// message for that, so a server error is not also reported as uncaught; any other error still is.
window.addEventListener("unhandledrejection", (event) => {
	if (event.reason?.exc_type) event.preventDefault()
})

loadBoot().then(
	() => createApp(App).use(router).mount("#app"),
	() => {
		// Only reachable on the dev server when signed out; one.py redirects guests in production
		window.location.href = `/login?redirect-to=${encodeURIComponent(window.location.pathname)}`
	},
)

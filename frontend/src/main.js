import "./index.css"
import { createApp } from "vue"
import { frappeRequest, setConfig } from "frappe-ui"
import App from "./App.vue"
import router from "./router"
import { loadBoot } from "./boot"

setConfig("resourceFetcher", frappeRequest)

loadBoot().then(
	() => createApp(App).use(router).mount("#app"),
	() => {
		// Only reachable on the dev server when signed out; one.py redirects guests in production
		window.location.href = `/login?redirect-to=${encodeURIComponent(window.location.pathname)}`
	},
)

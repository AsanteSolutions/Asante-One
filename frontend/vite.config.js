import path from "path"
import { defineConfig } from "vite"
import vue from "@vitejs/plugin-vue"
import frappeui from "frappe-ui/vite"

export default defineConfig({
	plugins: [
		frappeui({
			frontendRoute: "/one",
			frappeProxy: true,
			jinjaBootData: true,
			lucideIcons: false,
			buildConfig: {
				outDir: "../asante_one/public/frontend",
				indexHtmlPath: "../asante_one/www/one.html",
			},
		}),
		vue(),
	],
	resolve: {
		alias: { "@": path.resolve(__dirname, "src") },
	},
})

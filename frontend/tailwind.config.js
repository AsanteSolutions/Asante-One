// Colours are the prototype's CSS variables (src/index.css), so light and dark switch
// by changing the variables, not the classes.
const token = (name) => `var(--${name})`

/** @type {import('tailwindcss').Config} */
export default {
	content: ["./index.html", "./src/**/*.{vue,js}"],
	theme: {
		screens: {
			sm: "640px",
			// The prototype's breakpoints: rail and three columns above, tab bar below
			nav: "861px",
			wide: "1181px",
		},
		extend: {
			colors: {
				canvas: token("canvas"),
				surface: token("surface"),
				sunk: token("sunk"),
				ink: { DEFAULT: token("ink"), 2: token("ink-2") },
				grey: token("grey"),
				line: { DEFAULT: token("line"), 2: token("line-2") },
				accent: { DEFAULT: token("accent"), bg: token("accent-bg"), hover: token("accent-hover") },
				plum: token("plum"),
				lav: { DEFAULT: token("lav"), 2: token("lav-2") },
				ok: { DEFAULT: token("ok"), bg: token("ok-bg") },
				warn: { DEFAULT: token("warn"), bg: token("warn-bg") },
				risk: { DEFAULT: token("risk"), bg: token("risk-bg") },
				ph: { DEFAULT: token("ph"), bg: token("ph-bg") },
			},
			fontFamily: {
				display: token("display"),
				body: token("body"),
			},
			boxShadow: {
				sm: token("shadow-sm"),
				DEFAULT: token("shadow"),
			},
		},
	},
	plugins: [],
}

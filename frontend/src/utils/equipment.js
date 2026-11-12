import { formatDate } from "@/utils/dates"

// ERPNext quantities are floats; show 2, not 2.0
export const count = (n) => Math.round(n * 100) / 100

export function itemCount(items) {
	const n = count(items.reduce((sum, i) => sum + i.qty, 0))
	return `${n} item${n === 1 ? "" : "s"}`
}

export const outSince = (h) => [h.since && `Out since ${formatDate(h.since)}`, h.purpose].filter(Boolean).join(" · ")

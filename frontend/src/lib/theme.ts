export type Theme = "light" | "dark" | "system"

const KEY = "kamra-theme"

export const getTheme = (): Theme => {
  const t = localStorage.getItem(KEY)
  return t === "dark" || t === "system" ? t : "light"
}

const resolve = (t: Theme) =>
  t === "system"
    ? window.matchMedia("(prefers-color-scheme: dark)").matches
      ? "dark"
      : "light"
    : t

export function applyTheme(t: Theme) {
  document.documentElement.classList.toggle("dark", resolve(t) === "dark")
}

export function setTheme(t: Theme) {
  localStorage.setItem(KEY, t)
  applyTheme(t)
}

/** Call once at boot: applies the stored theme and follows OS changes
 * while in "system" mode. */
export function initTheme() {
  applyTheme(getTheme())
  window
    .matchMedia("(prefers-color-scheme: dark)")
    .addEventListener("change", () => {
      if (getTheme() === "system") applyTheme("system")
    })
}

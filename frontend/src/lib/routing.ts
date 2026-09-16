export const ROUTER_BASENAME =
  import.meta.env.VITE_ROUTER_BASENAME ??
  (import.meta.env.PROD ? "/kamra" : "/")

// Prefix an in-app path with the basename for a full-page navigation
// (window.location), which the router's own navigate() would otherwise add.
export function toFullPath(path: string): string {
  const base = ROUTER_BASENAME === "/" ? "" : ROUTER_BASENAME
  return base + (path.startsWith("/") ? path : "/" + path)
}

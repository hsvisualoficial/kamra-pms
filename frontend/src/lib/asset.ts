// Resolve a static asset shipped in frontend/public against the build base.
// Dev: BASE_URL is "/", so asset("kamra-mark.svg") -> "/kamra-mark.svg".
// Prod: BASE_URL is "/assets/kamra/frontend/", so the same call resolves to
// "/assets/kamra/frontend/kamra-mark.svg" (where Frappe serves it).
export const asset = (path: string) =>
  import.meta.env.BASE_URL + path.replace(/^\//, "")

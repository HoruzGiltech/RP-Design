// Una función por cada endpoint del backend (ver specs/design.md §2.7).

import { apiGet, apiPost } from './client'

/** Todo el contenido editable del sitio, en una sola llamada. */
export function getSite() {
  return apiGet('/site/')
}

/** Todos los proyectos publicados, en el orden del panel. */
export function getProjects() {
  return apiGet('/projects/')
}

/** Los proyectos destacados del inicio (máximo 3). */
export function getFeaturedProjects() {
  return apiGet('/projects/?featured=true')
}

/** Detalle de un proyecto con su galería. Lanza un ApiError 404 si no existe. */
export function getProject(slug) {
  return apiGet(`/projects/${encodeURIComponent(slug)}/`)
}

/** Una página legal ("terminos" o "privacidad") con sus apartados. */
export function getLegalPage(slug) {
  return apiGet(`/legal/${encodeURIComponent(slug)}/`)
}

/** Áreas a remodelar con su precio por m². */
export function getQuoteAreas() {
  return apiGet('/quote-areas/')
}

/** Envía una cotización. Devuelve el estimado y el enlace de WhatsApp. */
export function createQuote(quote) {
  return apiPost('/quotes/', quote)
}

// Una función por cada endpoint del backend (ver specs/design.md §2.7).

import { apiGet, apiPost } from './client'

/** Todo el contenido editable del sitio, en una sola llamada. */
export function getSite() {
  return apiGet('/site/')
}

/**
 * Proyectos publicados, en el orden del panel.
 * Con `categorySlug`, solo los de esa categoría.
 */
export function getProjects(categorySlug) {
  if (!categorySlug) return apiGet('/projects/')
  return apiGet(`/projects/?category=${encodeURIComponent(categorySlug)}`)
}

/** Los proyectos cuya portada va en el hero del inicio (máximo 6). */
export function getHeroProjects() {
  return apiGet('/projects/?hero=true')
}

/** Categorías que tienen proyectos publicados, con su portada y su cantidad. */
export function getProjectCategories() {
  return apiGet('/project-categories/')
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

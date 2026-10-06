import { useEffect } from 'react'

import { useSite } from '../context/SiteContext'

/** Devuelve la etiqueta <meta name="description">; la crea si no existe. */
function getDescriptionTag() {
  let tag = document.querySelector('meta[name="description"]')
  if (!tag) {
    tag = document.createElement('meta')
    tag.name = 'description'
    document.head.appendChild(tag)
  }
  return tag
}

/**
 * Pone el título de la pestaña y la descripción de la página.
 *
 *   useDocumentTitle()                       -> "RP Diseño Interior"
 *   useDocumentTitle('Proyectos')            -> "Proyectos | RP Diseño Interior"
 *   useDocumentTitle(project.title, resumen) -> además cambia la descripción
 *
 * El nombre del sitio y la descripción general salen de "SEO" en el panel.
 */
export function useDocumentTitle(pageTitle, pageDescription) {
  const { data: site } = useSite()
  const siteTitle = site.seo.site_title
  const description = pageDescription || site.seo.meta_description

  useEffect(() => {
    document.title = pageTitle ? `${pageTitle} | ${siteTitle}` : siteTitle
    getDescriptionTag().content = description
  }, [pageTitle, siteTitle, description])
}

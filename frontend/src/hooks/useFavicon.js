import { useEffect } from 'react'

/** Lee el valor de una variable CSS de tokens.css, por ejemplo "--color-text". */
function getToken(name) {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim()
}

/**
 * Dibuja el mismo círculo con iniciales del encabezado, como imagen SVG.
 * Un favicon no puede usar las fuentes del sitio, así que usa la del sistema.
 */
function buildInitialsIcon(initials) {
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
      <circle cx="32" cy="32" r="32" fill="${getToken('--color-text')}" />
      <text x="32" y="33" fill="${getToken('--color-bg')}" font-family="Arial Narrow, Arial, sans-serif"
        font-size="26" font-weight="700" text-anchor="middle" dominant-baseline="middle">${initials}</text>
    </svg>`
  return `data:image/svg+xml,${encodeURIComponent(svg)}`
}

/**
 * Pone el icono de la pestaña del navegador (favicon) con el logo del panel.
 * Si el cliente no subió un logo, usa el círculo con las iniciales.
 */
export function useFavicon(settings) {
  const logo = settings?.logo
  const initials = settings?.brand_initials

  useEffect(() => {
    if (!logo && !initials) return

    let link = document.querySelector('link[rel="icon"]')
    if (!link) {
      link = document.createElement('link')
      link.rel = 'icon'
      document.head.appendChild(link)
    }
    link.href = logo || buildInitialsIcon(initials)
  }, [logo, initials])
}

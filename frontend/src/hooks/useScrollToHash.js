import { useEffect } from 'react'
import { useLocation } from 'react-router-dom'

/**
 * React Router cambia de página sin recargar, así que el navegador no hace
 * su trabajo habitual con el scroll. Este hook lo repone:
 *   - si la URL trae un ancla (/#servicios), baja hasta esa sección;
 *   - si no, sube al inicio de la página nueva.
 */
export function useScrollToHash() {
  const { pathname, hash } = useLocation()

  useEffect(() => {
    if (!hash) {
      window.scrollTo(0, 0)
      return
    }
    // decodeURIComponent: un ancla con tildes llega codificada en la URL
    const section = document.getElementById(decodeURIComponent(hash.slice(1)))
    if (section) section.scrollIntoView()
  }, [pathname, hash])
}

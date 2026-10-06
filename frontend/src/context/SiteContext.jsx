import { createContext, useContext } from 'react'

import { getSite } from '../api/endpoints'
import { useFetch } from '../hooks/useFetch'

/*
  El contenido del sitio (/api/site/) lo necesitan casi todos los componentes:
  encabezado, pie, cada sección del inicio... Se pide una sola vez aquí y se
  comparte con Context, en lugar de pedirlo en cada componente.
*/
const SiteContext = createContext(null)

export function SiteProvider({ children }) {
  // value = { data, loading, error, reload }
  const site = useFetch(getSite)

  return <SiteContext.Provider value={site}>{children}</SiteContext.Provider>
}

/** Devuelve { data, loading, error, reload } del contenido del sitio. */
// oxlint-disable-next-line react/only-export-components
export function useSite() {
  const site = useContext(SiteContext)
  if (site === null) {
    throw new Error('useSite solo funciona dentro de <SiteProvider>.')
  }
  return site
}

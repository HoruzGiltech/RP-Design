import { Outlet } from 'react-router-dom'

import { useSite } from '../../context/SiteContext'
import { useAccentColor } from '../../hooks/useAccentColor'
import { useFavicon } from '../../hooks/useFavicon'
import { useScrollToHash } from '../../hooks/useScrollToHash'
import ErrorMessage from '../ui/ErrorMessage'
import Spinner from '../ui/Spinner'
import Footer from './Footer'
import Header from './Header'
import WhatsAppButton from './WhatsAppButton'
import './Layout.css'

const MAIN_ID = 'contenido'

/**
 * Marco común de todas las páginas: encabezado, contenido y pie.
 *
 * Espera aquí a que llegue el contenido del sitio. Así las páginas y los
 * componentes de dentro pueden usar useSite() sabiendo que `data` ya existe.
 */
export default function Layout() {
  const { data: site, loading, error, reload } = useSite()

  useFavicon(site?.settings)
  useAccentColor(site?.settings.accent_color)

  if (loading) return <Spinner />
  if (error) return <ErrorMessage message={error.message} onRetry={reload} />

  return <SiteFrame />
}

/** Lo que se dibuja cuando el contenido del sitio ya llegó. */
function SiteFrame() {
  useScrollToHash()

  return (
    <div className="layout">
      {/* Primer elemento al tabular: deja saltar el menú a quien navega con teclado */}
      <a className="layout__skip-link" href={`#${MAIN_ID}`}>
        Saltar al contenido
      </a>
      <Header />
      <main id={MAIN_ID} className="layout__main" tabIndex={-1}>
        <Outlet />
      </main>
      <Footer />
      <WhatsAppButton />
    </div>
  )
}

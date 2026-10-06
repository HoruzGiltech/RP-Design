import { Link } from 'react-router-dom'

import { useSite } from '../../context/SiteContext'
import './Footer.css'

// El año se calcula solo: no hay que acordarse de cambiarlo cada enero
const CURRENT_YEAR = new Date().getFullYear()

// Crédito de quien desarrolló el sitio. Es el único texto fijo del pie:
// no es contenido del cliente, por eso no se edita desde el panel.
const DEVELOPER_CREDIT = 'Desarrollado por Giltechnology'

export default function Footer() {
  const { data: site } = useSite()
  const { footer, legal_pages: legalPages } = site

  if (!footer.is_visible) return null

  return (
    <footer className="footer">
      <div className="container footer__inner">
        <div className="footer__row">
          <span className="footer__name">{footer.name}</span>
          {footer.tagline && <span>{footer.tagline}</span>}
          <span>© {CURRENT_YEAR}</span>
        </div>

        <div className="footer__row footer__row--secondary">
          <nav aria-label="Legal" className="footer__legal">
            {legalPages.map((page) => (
              <Link key={page.slug} to={`/${page.slug}`} className="footer__link">
                {page.title}
              </Link>
            ))}
          </nav>
          <span>{DEVELOPER_CREDIT}</span>
        </div>
      </div>
    </footer>
  )
}

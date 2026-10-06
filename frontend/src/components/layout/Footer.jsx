import { useSite } from '../../context/SiteContext'
import './Footer.css'

// El año se calcula solo: no hay que acordarse de cambiarlo cada enero
const CURRENT_YEAR = new Date().getFullYear()

export default function Footer() {
  const { data: site } = useSite()
  const { footer } = site

  if (!footer.is_visible) return null

  return (
    <footer className="footer">
      <div className="container footer__inner">
        <span className="footer__name">{footer.name}</span>
        {footer.tagline && <span>{footer.tagline}</span>}
        <span>© {CURRENT_YEAR}</span>
      </div>
    </footer>
  )
}

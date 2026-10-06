import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import { useSite } from '../../context/SiteContext'
import Button from '../ui/Button'
import './Header.css'

const MENU_ID = 'menu-principal'

/**
 * Enlaces del menú. Son fijos (specs/requirements.md §3, S1), pero cada uno
 * solo se muestra si su sección está visible en el sitio.
 */
function getNavLinks(site) {
  return [
    { label: 'Servicios', to: '/#servicios', isVisible: site.services.is_visible },
    { label: 'Proyectos', to: '/#proyectos', isVisible: site.projects_section.is_visible },
    { label: 'Proceso', to: '/#proceso', isVisible: site.process.is_visible },
  ].filter((link) => link.isVisible)
}

export default function Header() {
  const { data: site } = useSite()
  // Solo importa en móvil: en escritorio el menú siempre está a la vista
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  // El menú móvil también se cierra con la tecla Escape
  useEffect(() => {
    if (!isMenuOpen) return undefined

    function closeOnEscape(event) {
      if (event.key === 'Escape') setIsMenuOpen(false)
    }
    document.addEventListener('keydown', closeOnEscape)
    return () => document.removeEventListener('keydown', closeOnEscape)
  }, [isMenuOpen])

  const { settings } = site
  const navLinks = getNavLinks(site)

  return (
    <header className="header">
      <div className="container header__inner">
        <Link to="/#inicio" className="header__brand" onClick={() => setIsMenuOpen(false)}>
          {settings.logo ? (
            <img className="header__logo-image" src={settings.logo} alt="" />
          ) : (
            <span className="header__logo-circle" aria-hidden="true">
              {settings.brand_initials}
            </span>
          )}
          <span className="header__brand-text">
            <span className="header__brand-name">{settings.brand_name}</span>
            <span className="header__brand-subtitle">{settings.brand_subtitle}</span>
          </span>
        </Link>

        <button
          type="button"
          className="header__toggle"
          aria-expanded={isMenuOpen}
          aria-controls={MENU_ID}
          onClick={() => setIsMenuOpen((isOpen) => !isOpen)}
        >
          <span className="visually-hidden">{isMenuOpen ? 'Cerrar menú' : 'Abrir menú'}</span>
          <span className="header__toggle-icon" aria-hidden="true" />
        </button>

        <nav
          id={MENU_ID}
          aria-label="Principal"
          className={isMenuOpen ? 'header__nav is-open' : 'header__nav'}
          // Al elegir cualquier enlace, el menú móvil se cierra
          onClick={() => setIsMenuOpen(false)}
        >
          {navLinks.map((link) => (
            <Link key={link.to} to={link.to} className="header__link">
              {link.label}
            </Link>
          ))}
          {site.contact.is_visible && (
            <Button to="/#contacto" size="small" className="header__cta">
              {settings.header_cta_text}
            </Button>
          )}
        </nav>
      </div>
    </header>
  )
}

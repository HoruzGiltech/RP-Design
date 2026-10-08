import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'

import { useSite } from '../../context/SiteContext'
import { useHideOnScroll } from '../../hooks/useHideOnScroll'
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

/**
 * Encabezado del sitio (specs-002, RF-13).
 * - Las opciones del menú van siempre detrás de un botón, que va a la
 *   izquierda del logo. Las opciones se despliegan debajo, en todos los
 *   tamaños de pantalla.
 * - Se oculta al bajar por la página y vuelve al subir.
 */
export default function Header() {
  const { data: site } = useSite()
  const headerRef = useRef(null)
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  // Con el menú abierto no se oculta: se quedaría un menú flotando sin encabezado
  const isHidden = useHideOnScroll({ disabled: isMenuOpen })

  // Con el menú abierto: se cierra con Escape o al pulsar fuera del encabezado
  useEffect(() => {
    if (!isMenuOpen) return undefined

    function closeOnEscape(event) {
      if (event.key === 'Escape') setIsMenuOpen(false)
    }
    function closeOnOutsidePress(event) {
      if (!headerRef.current.contains(event.target)) setIsMenuOpen(false)
    }
    document.addEventListener('keydown', closeOnEscape)
    document.addEventListener('pointerdown', closeOnOutsidePress)
    return () => {
      document.removeEventListener('keydown', closeOnEscape)
      document.removeEventListener('pointerdown', closeOnOutsidePress)
    }
  }, [isMenuOpen])

  const { settings } = site
  const navLinks = getNavLinks(site)
  const showCta = site.contact.is_visible

  function closeMenu() {
    setIsMenuOpen(false)
  }

  return (
    <header ref={headerRef} className={isHidden ? 'header is-hidden' : 'header'}>
      <div className="container header__bar">
        {/* Lado izquierdo: el botón del menú y, a su derecha, el logo */}
        <div className="header__left">
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

          <Link to="/#inicio" className="header__brand" onClick={closeMenu}>
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
        </div>

        {/* En pantallas anchas el botón de cotizar sigue a la vista, a la derecha */}
        {showCta && (
          <Button
            to="/#contacto"
            size="small"
            className="header__cta header__cta--bar"
            onClick={closeMenu}
          >
            {settings.header_cta_text}
          </Button>
        )}
      </div>

      {/* Las opciones se despliegan debajo del encabezado, alineadas con el botón */}
      <nav
        id={MENU_ID}
        aria-label="Principal"
        className={isMenuOpen ? 'header__menu is-open' : 'header__menu'}
        // Al elegir cualquier opción, el menú se cierra
        onClick={closeMenu}
      >
        <div className="container header__menu-inner">
          {navLinks.map((link) => (
            <Link key={link.to} to={link.to} className="header__link">
              {link.label}
            </Link>
          ))}
          {/* En pantallas angostas el botón de cotizar va dentro del menú, como antes */}
          {showCta && (
            <Button to="/#contacto" size="small" className="header__cta header__cta--menu">
              {settings.header_cta_text}
            </Button>
          )}
        </div>
      </nav>
    </header>
  )
}

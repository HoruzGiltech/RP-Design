import { useEffect, useState } from 'react'
import { useLocation } from 'react-router-dom'

import { useSite } from '../../context/SiteContext'
import { buildWhatsAppLink } from '../../utils/whatsapp'
import { WhatsAppIcon } from '../ui/Icons'
import './WhatsAppButton.css'

// Sección del inicio donde está el formulario de cotización
const CONTACT_SECTION_ID = 'contacto'

/**
 * Dice si la sección Contacto está a la vista. Mientras lo está, el botón
 * flotante se oculta: ahí ya están el formulario y el enlace de WhatsApp, y
 * el botón taparía el de "Enviar".
 */
function useIsContactVisible() {
  const { pathname } = useLocation()
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    const section = document.getElementById(CONTACT_SECTION_ID)
    // Solo el inicio tiene esa sección; en las demás páginas no hay nada que vigilar
    if (!section || !('IntersectionObserver' in window)) return undefined

    const observer = new IntersectionObserver(([entry]) => setIsVisible(entry.isIntersecting))
    observer.observe(section)

    return () => {
      observer.disconnect()
      setIsVisible(false)
    }
    // Al cambiar de página se vuelve a buscar la sección
  }, [pathname])

  return isVisible
}

/**
 * Botón flotante de WhatsApp, fijo abajo a la derecha en todas las páginas
 * (specs-001, RF-12). Abre el chat con el mensaje configurado en el panel.
 */
export default function WhatsAppButton() {
  const { data: site } = useSite()
  const isContactVisible = useIsContactVisible()
  const { settings } = site

  if (!settings.show_whatsapp_button || !settings.whatsapp_number) return null

  return (
    <a
      className={isContactVisible ? 'whatsapp-button is-hidden' : 'whatsapp-button'}
      href={buildWhatsAppLink(settings.whatsapp_number, settings.whatsapp_greeting)}
      target="_blank"
      rel="noopener noreferrer"
      aria-label="Escribir por WhatsApp"
      // Oculto no debe poder enfocarse con el teclado
      tabIndex={isContactVisible ? -1 : undefined}
      aria-hidden={isContactVisible ? 'true' : undefined}
    >
      <WhatsAppIcon className="whatsapp-button__icon" />
    </a>
  )
}

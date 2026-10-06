import { useSite } from '../../context/SiteContext'
import { buildWhatsAppLink } from '../../utils/whatsapp'
import './ContactInfo.css'

/** Datos de contacto. Salen de "Configuración general" del panel. */
export default function ContactInfo() {
  const { data: site } = useSite()
  const { settings } = site

  return (
    <address className="contact-info">
      {settings.whatsapp_number && (
        <a
          className="contact-info__whatsapp"
          href={buildWhatsAppLink(settings.whatsapp_number)}
          target="_blank"
          rel="noopener noreferrer"
        >
          WhatsApp: {settings.whatsapp_display}
        </a>
      )}
      {settings.contact_email && (
        <a href={`mailto:${settings.contact_email}`}>{settings.contact_email}</a>
      )}
      {settings.instagram_url && (
        <a href={settings.instagram_url} target="_blank" rel="noopener noreferrer">
          Instagram @{settings.instagram_handle}
        </a>
      )}
      {settings.city && <span className="contact-info__city">{settings.city}</span>}
    </address>
  )
}

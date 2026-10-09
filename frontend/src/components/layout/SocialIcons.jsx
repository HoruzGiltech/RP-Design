import { useSite } from '../../context/SiteContext'
import { buildWhatsAppLink } from '../../utils/whatsapp'
import { InstagramIcon, MailIcon, WhatsAppIcon } from '../ui/Icons'

/**
 * Iconos de contacto del pie: WhatsApp, correo e Instagram (specs-003, RF-33).
 * Los datos salen de "Configuración general" del panel; si falta alguno,
 * su icono no se muestra.
 */
export default function SocialIcons() {
  const { data: site } = useSite()
  const { settings } = site

  const links = [
    settings.whatsapp_number && {
      key: 'whatsapp',
      href: buildWhatsAppLink(settings.whatsapp_number),
      // Como el icono no tiene texto, este es el nombre que lee un lector de pantalla
      label: `WhatsApp: ${settings.whatsapp_display}`,
      Icon: WhatsAppIcon,
      opensNewTab: true,
    },
    settings.contact_email && {
      key: 'email',
      href: `mailto:${settings.contact_email}`,
      label: `Correo: ${settings.contact_email}`,
      Icon: MailIcon,
      opensNewTab: false,
    },
    settings.instagram_url && {
      key: 'instagram',
      href: settings.instagram_url,
      label: `Instagram: @${settings.instagram_handle}`,
      Icon: InstagramIcon,
      opensNewTab: true,
    },
  ].filter(Boolean)

  if (links.length === 0) return null

  return (
    <ul className="footer__social">
      {links.map(({ key, href, label, Icon, opensNewTab }) => (
        <li key={key}>
          <a
            className="footer__social-link"
            href={href}
            aria-label={label}
            // title: quien usa mouse ve el dato al pasar el cursor
            title={label}
            target={opensNewTab ? '_blank' : undefined}
            rel={opensNewTab ? 'noopener noreferrer' : undefined}
          >
            <Icon className="footer__social-icon" />
          </a>
        </li>
      ))}
    </ul>
  )
}

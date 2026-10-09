import { useSite } from '../../context/SiteContext'
import Reveal from '../ui/Reveal'
import Section from '../ui/Section'
import './Contact.css'

/**
 * Sección Contacto, en una sola columna (specs-002, RF-18): título e
 * introducción y el formulario a todo el ancho. Los datos de contacto están
 * en el pie de página (specs-003, RF-33).
 *
 * `children` es el formulario de cotización (components/quote/QuoteCalculator).
 */
export default function Contact({ children }) {
  const { data: site } = useSite()
  const { contact } = site

  if (!contact.is_visible) return null

  return (
    <Section id="contacto" variant="alt" className="contact">
      <div className="contact__header">
        <Reveal as="h2">{contact.title}</Reveal>
        {contact.intro && (
          <Reveal as="p" index={1} className="contact__intro">
            {contact.intro}
          </Reveal>
        )}
      </div>

      {children && <div>{children}</div>}
    </Section>
  )
}

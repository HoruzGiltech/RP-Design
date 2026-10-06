import { useSite } from '../../context/SiteContext'
import Reveal from '../ui/Reveal'
import Section from '../ui/Section'
import ContactInfo from './ContactInfo'
import './Contact.css'

/**
 * Sección Contacto: a la izquierda los datos, a la derecha el formulario.
 * `children` es el formulario de cotización (components/quote/QuoteCalculator).
 */
export default function Contact({ children }) {
  const { data: site } = useSite()
  const { contact } = site

  if (!contact.is_visible) return null

  return (
    <Section id="contacto" variant="alt" className="contact">
      <div className="contact__info-column">
        <Reveal as="h2">{contact.title}</Reveal>
        {contact.intro && (
          <Reveal as="p" index={1} className="contact__intro">
            {contact.intro}
          </Reveal>
        )}
        <Reveal index={2}>
          <ContactInfo />
        </Reveal>
      </div>

      {children && <div>{children}</div>}
    </Section>
  )
}

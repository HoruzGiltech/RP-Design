import { useSite } from '../../context/SiteContext'
import Reveal from '../ui/Reveal'
import Section from '../ui/Section'
import ServiceCard from './ServiceCard'
import '../projects/ProjectGrid.css'
import './Services.css'

/**
 * Sección Servicios: una cuadrícula de tarjetas con portada sobre fondo
 * oscuro, con el aspecto que tenía la sección Proyectos (specs-004, RF-35).
 */
export default function Services() {
  const { data: site } = useSite()
  const { services } = site

  // Oculta desde el panel, o sin servicios que mostrar: no se deja un título suelto
  if (!services.is_visible || services.items.length === 0) return null

  // El botón lleva al formulario: sin sección Contacto no se muestra
  const ctaText = site.contact.is_visible ? services.cta_text : ''

  return (
    <Section id="servicios" variant="dark" className="services">
      <div className="services__header">
        <Reveal as="h2">{services.title}</Reveal>
        {services.intro && (
          <Reveal as="p" index={1} className="services__intro">
            {services.intro}
          </Reveal>
        )}
      </div>

      {/* La misma cuadrícula de las tarjetas de proyecto */}
      <div className="project-grid">
        {services.items.map((service, position) => (
          <ServiceCard key={service.id} service={service} index={position} ctaText={ctaText} />
        ))}
      </div>
    </Section>
  )
}

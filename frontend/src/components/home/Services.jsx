import { useSite } from '../../context/SiteContext'
import Reveal from '../ui/Reveal'
import Section from '../ui/Section'
import ServiceCard from './ServiceCard'
import './Services.css'

// Cuántas tarjetas caben, como máximo, en una fila en escritorio
const MAX_COLUMNS = 4

/**
 * Sección Servicios: una cuadrícula de tarjetas con portada sobre fondo
 * oscuro (specs-004, RF-35).
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

      {/*
        Hasta 4 tarjetas por fila (specs-005, RF-44). Con menos de 4 servicios,
        las columnas son las justas para que no quede un hueco al final.
      */}
      <div
        className="services__grid"
        style={{ '--service-columns': Math.min(services.items.length, MAX_COLUMNS) }}
      >
        {services.items.map((service, position) => (
          <ServiceCard key={service.id} service={service} index={position} ctaText={ctaText} />
        ))}
      </div>
    </Section>
  )
}

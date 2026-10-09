import { useSite } from '../../context/SiteContext'
import Button from '../ui/Button'
import Reveal from '../ui/Reveal'
import Section from '../ui/Section'
import './Services.css'

/** 0 -> "01", 1 -> "02"... El número sale de la posición, no se guarda en el panel. */
function formatNumber(position) {
  return String(position + 1).padStart(2, '0')
}

/**
 * En escritorio, la primera tarjeta entra desde la izquierda, la última desde
 * la derecha y las del medio desde abajo. (En móvil todas entran desde abajo:
 * eso lo resuelve Services.css.)
 */
function getDirection(position, total) {
  if (total < 2) return 'bottom'
  if (position === 0) return 'left'
  if (position === total - 1) return 'right'
  return 'bottom'
}

export default function Services() {
  const { data: site } = useSite()
  const { services } = site

  // Oculta desde el panel, o sin servicios que mostrar: no se deja un título suelto
  if (!services.is_visible || services.items.length === 0) return null

  // El botón lleva al formulario: sin sección Contacto (o sin texto) no se muestra
  const showCta = site.contact.is_visible && Boolean(services.cta_text)

  return (
    <Section id="servicios" className="services">
      <div className="services__header">
        <Reveal as="h2">{services.title}</Reveal>
        {services.intro && (
          <Reveal as="p" index={1} className="services__intro">
            {services.intro}
          </Reveal>
        )}
      </div>

      <div className="services__grid">
        {services.items.map((service, position) => (
          <Reveal
            as="article"
            key={service.id}
            className="services__card"
            from={getDirection(position, services.items.length)}
            index={position}
          >
            <span className="services__number" aria-hidden="true">
              {formatNumber(position)}
            </span>
            <h3 className="services__title">{service.title}</h3>
            <p className="services__description">{service.description}</p>
            {showCta && (
              <Button
                to="/#contacto"
                size="small"
                className="services__cta"
                // Varias tarjetas tienen el mismo botón: el nombre dice de cuál es
                aria-label={`${services.cta_text}: ${service.title}`}
              >
                {services.cta_text}
              </Button>
            )}
          </Reveal>
        ))}
      </div>
    </Section>
  )
}

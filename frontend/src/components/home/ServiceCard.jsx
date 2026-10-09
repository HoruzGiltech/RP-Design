import MediaPlaceholder from '../media/MediaPlaceholder'
import Button from '../ui/Button'
import Reveal from '../ui/Reveal'
import '../../styles/overlay.css'

/** 0 -> "01", 1 -> "02"... El número sale de la posición, no se guarda en el panel. */
function formatNumber(position) {
  return String(position + 1).padStart(2, '0')
}

/**
 * Tarjeta de un servicio: su portada, su número y su título (specs-004, RF-35).
 * Sobre la portada hay una capa con la descripción y el botón "Cotizar": con
 * mouse aparece al pasar el cursor, y en pantallas táctiles entra sola cuando
 * la tarjeta aparece en pantalla (ver styles/overlay.css).
 *
 * service: el servicio (objeto de la API)
 * index:   posición en la cuadrícula; da el número y el orden de entrada
 * ctaText: texto del botón "Cotizar", o '' si no se debe mostrar
 */
export default function ServiceCard({ service, index, ctaText }) {
  return (
    <Reveal as="article" index={index} className="service-card">
      <div className="service-card__media has-cover-overlay">
        {service.image ? (
          <img
            className="service-card__image"
            src={service.image}
            alt={service.image_alt}
            // Las tarjetas que están más abajo no se descargan hasta que hacen falta
            loading="lazy"
          />
        ) : (
          // Sin imagen cargada en el panel queda un fondo liso
          <MediaPlaceholder variant="dark" />
        )}

        <div className="cover-overlay cover-overlay--auto">
          <div className="cover-overlay__content">
            <p className="cover-overlay__text">{service.description}</p>
            {ctaText && (
              <Button
                to="/#contacto"
                size="small"
                onDark
                // Varias tarjetas tienen el mismo botón: el nombre dice de cuál es
                aria-label={`${ctaText}: ${service.title}`}
              >
                {ctaText}
              </Button>
            )}
          </div>
        </div>

        <span className="service-card__number" aria-hidden="true">
          {formatNumber(index)}
        </span>
      </div>

      <h3 className="service-card__title">{service.title}</h3>
    </Reveal>
  )
}

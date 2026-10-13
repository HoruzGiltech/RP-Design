import { useInCenter } from '../../hooks/useInCenter'
import MediaPlaceholder from '../media/MediaPlaceholder'
import Button from '../ui/Button'
import Reveal from '../ui/Reveal'
import '../../styles/overlay.css'

/**
 * Tarjeta de un servicio: su portada y su título, sin número (specs-008, RF-60).
 * Sobre la portada hay una capa con la descripción y el botón "Cotizar": con
 * mouse aparece al pasar el cursor, y en pantallas táctiles cuando la tarjeta
 * cruza el centro de la pantalla (ver styles/overlay.css y useInCenter).
 *
 * service: el servicio (objeto de la API)
 * index:   posición en la cuadrícula; da el orden de entrada
 * ctaText: texto del botón "Cotizar", o '' si no se debe mostrar
 */
export default function ServiceCard({ service, index, ctaText }) {
  // La descripción solo se lee en la capa: con "reducir movimiento" queda fija
  const { ref, isInCenter } = useInCenter({ alwaysWhenReduced: true })
  const mediaClasses = ['service-card__media', 'has-cover-overlay', isInCenter ? 'is-centered' : '']
    .filter(Boolean)
    .join(' ')

  return (
    <Reveal as="article" index={index} className="service-card">
      <div ref={ref} className={mediaClasses}>
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

        <div className="cover-overlay">
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
      </div>

      <h3 className="service-card__title">{service.title}</h3>
    </Reveal>
  )
}

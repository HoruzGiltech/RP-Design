import { useState } from 'react'

import Reveal from '../ui/Reveal'
import Lightbox from './Lightbox'
import './MediaGallery.css'

/**
 * Galería de un proyecto, en el orden que el cliente definió en el panel.
 * - Las imágenes muestran su miniatura y se abren en grande en el visor.
 * - Los videos se reproducen en su sitio, con controles y sin arrancar solos.
 */
export default function MediaGallery({ media }) {
  // Posición (dentro de `images`) de la imagen abierta en el visor; null = cerrado
  const [openIndex, setOpenIndex] = useState(null)

  // El visor solo recorre imágenes, así que se separan de los videos
  const images = media.filter((item) => item.media_type === 'image')

  if (media.length === 0) return null

  return (
    <>
      <ul className="media-gallery">
        {media.map((item, position) => (
          <Reveal as="li" key={item.id} index={position % 3} className="media-gallery__item">
            {item.media_type === 'video' ? (
              <video
                className="media-gallery__media"
                src={item.file}
                poster={item.poster || undefined}
                aria-label={item.alt_text}
                controls
                preload="metadata"
                playsInline
              />
            ) : (
              <button
                type="button"
                className="media-gallery__button"
                onClick={() => setOpenIndex(images.indexOf(item))}
              >
                <img
                  className="media-gallery__media"
                  src={item.thumbnail || item.file}
                  alt={item.alt_text}
                  loading="lazy"
                />
                <span className="visually-hidden">Ver en grande</span>
              </button>
            )}
          </Reveal>
        ))}
      </ul>

      {openIndex !== null && (
        <Lightbox
          images={images}
          index={openIndex}
          onNavigate={setOpenIndex}
          onClose={() => setOpenIndex(null)}
        />
      )}
    </>
  )
}

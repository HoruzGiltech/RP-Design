import { useSite } from '../../context/SiteContext'
import { prefersReducedMotion } from '../../hooks/useReveal'
import MediaPlaceholder from '../media/MediaPlaceholder'
import Button from '../ui/Button'
import Reveal from '../ui/Reveal'
import './Hero.css'

/** Foto, video o recuadro liso de la Portada, según lo que haya subido el cliente. */
function HeroMedia({ hero }) {
  // Con "reducir movimiento" no se reproduce nada solo: se muestra la foto
  const showVideo = hero.video && !prefersReducedMotion()

  if (showVideo) {
    return (
      <video
        className="hero__media-item zoom-on-scroll"
        src={hero.video}
        // La foto se ve mientras el video carga
        poster={hero.image || undefined}
        aria-label={hero.image_alt || undefined}
        autoPlay
        muted
        loop
        playsInline
        preload="metadata"
      />
    )
  }
  if (hero.image) {
    return (
      <img
        className="hero__media-item zoom-on-scroll"
        src={hero.image}
        alt={hero.image_alt}
        // Es la imagen más importante de la página: se carga primero
        fetchPriority="high"
      />
    )
  }
  return <MediaPlaceholder variant="dark" />
}

export default function Hero() {
  const { data: site } = useSite()
  const { hero } = site

  if (!hero.is_visible) return null

  return (
    <section id="inicio" className="container hero">
      <div className="hero__text">
        {hero.eyebrow && (
          <Reveal as="p" className="hero__eyebrow">
            {hero.eyebrow}
          </Reveal>
        )}
        <Reveal as="h1" index={1}>
          {hero.title}
        </Reveal>
        {hero.body && (
          <Reveal as="p" index={2} className="hero__body">
            {hero.body}
          </Reveal>
        )}
        {/* Los botones entran desde la derecha, después del título */}
        <Reveal from="right" index={3} className="hero__actions">
          {site.contact.is_visible && <Button to="/#contacto">{hero.primary_cta_text}</Button>}
          {site.projects_section.is_visible && (
            <Button to="/#proyectos" variant="secondary">
              {hero.secondary_cta_text}
            </Button>
          )}
        </Reveal>
      </div>

      <div className="hero__media">
        <HeroMedia hero={hero} />
      </div>
    </section>
  )
}

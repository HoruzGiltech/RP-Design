import { getHeroProjects } from '../../api/endpoints'
import { useSite } from '../../context/SiteContext'
import { useFetch } from '../../hooks/useFetch'
import { prefersReducedMotion } from '../../hooks/useReveal'
import { useSlideshow } from '../../hooks/useSlideshow'
import Button from '../ui/Button'
import Reveal from '../ui/Reveal'
import HeroControls from './HeroControls'
import HeroSlides from './HeroSlides'
import './Hero.css'

// Tiempo que se ve cada portada. Debe coincidir con --slide-duration de tokens.css,
// que es lo que dura el zoom lento de la foto.
const SLIDE_INTERVAL_MS = 6000

/**
 * Fondo de respaldo: se usa cuando ningún proyecto tiene marcado
 * "Mostrar en el hero". Es la imagen o el video de la Portada del panel.
 */
function HeroFallback({ hero }) {
  // Con "reducir movimiento" no se reproduce nada solo: se muestra la foto
  if (hero.video && !prefersReducedMotion()) {
    return (
      <video
        className="hero__slide is-active"
        src={hero.video}
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
        className="hero__slide is-active"
        src={hero.image}
        alt={hero.image_alt}
        fetchPriority="high"
      />
    )
  }
  // Sin nada que mostrar queda el fondo oscuro de la sección
  return null
}

/** Hero del inicio: las portadas de los proyectos elegidos en el panel (specs-001, RF-08). */
export default function Hero() {
  const { data: site } = useSite()
  const { data: projects } = useFetch(getHeroProjects)

  // Mientras carga, o si la petición falla, no hay portadas: se usa el respaldo
  const slides = projects ?? []
  const slideshow = useSlideshow(slides.length, SLIDE_INTERVAL_MS)

  const { hero } = site
  if (!hero.is_visible) return null

  const hasSlides = slides.length > 0
  // Cada botón se muestra si el cliente lo dejó activado en el panel (specs-002,
  // RF-14) y si la sección a la que lleva está visible.
  const showPrimaryCta = hero.show_primary_cta && site.contact.is_visible
  const showSecondaryCta = hero.show_secondary_cta && site.projects_section.is_visible

  return (
    <section
      id="inicio"
      className="hero"
      // La rotación se detiene mientras el cursor o el foco del teclado están encima
      onMouseEnter={() => slideshow.hold(true)}
      onMouseLeave={() => slideshow.hold(false)}
      onFocus={() => slideshow.hold(true)}
      onBlur={() => slideshow.hold(false)}
    >
      <div
        className="hero__background"
        // Para lectores de pantalla: con varias portadas, esto es un grupo de imágenes que rota
        role={slideshow.canRotate ? 'group' : undefined}
        aria-roledescription={slideshow.canRotate ? 'carrusel' : undefined}
        aria-label={slideshow.canRotate ? 'Proyectos' : undefined}
      >
        {hasSlides ? (
          <HeroSlides
            slides={slides}
            index={slideshow.index}
            previousIndex={slideshow.previousIndex}
          />
        ) : (
          <HeroFallback hero={hero} />
        )}
        {/* Capa oscura: asegura que el texto se lea sobre cualquier foto */}
        <div className="hero__shade" aria-hidden="true" />
      </div>

      <div className="container hero__content">
        <div className="hero__text">
          {hero.eyebrow && (
            <Reveal as="p" className="hero__eyebrow">
              {hero.eyebrow}
            </Reveal>
          )}
          {hero.title ? (
            <Reveal as="h1" index={1}>
              {hero.title}
            </Reveal>
          ) : (
            // El cliente quitó el título, pero toda página necesita un título
            // principal para lectores de pantalla y buscadores: va oculto a la vista.
            <h1 className="visually-hidden">{site.seo.site_title}</h1>
          )}
          {hero.body && (
            <Reveal as="p" index={2} className="hero__body">
              {hero.body}
            </Reveal>
          )}
          {(showPrimaryCta || showSecondaryCta) && (
            <Reveal index={3} className="hero__actions">
              {showPrimaryCta && (
                <Button to="/#contacto" onDark>
                  {hero.primary_cta_text}
                </Button>
              )}
              {showSecondaryCta && (
                <Button to="/#proyectos" variant="secondary" onDark>
                  {hero.secondary_cta_text}
                </Button>
              )}
            </Reveal>
          )}
        </div>

        {hasSlides && <HeroControls slides={slides} slideshow={slideshow} />}
      </div>
    </section>
  )
}

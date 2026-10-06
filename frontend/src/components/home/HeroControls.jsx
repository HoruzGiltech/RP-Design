import { Link } from 'react-router-dom'

/**
 * Parte inferior del hero: el proyecto que se está viendo (con su enlace) y,
 * si hay más de una portada, los controles para pasar, pausar e ir a una.
 *
 * slides:    proyectos del hero
 * slideshow: lo que devuelve useSlideshow
 */
export default function HeroControls({ slides, slideshow }) {
  const { index, isPlaying, canRotate } = slideshow
  const project = slides[index]

  return (
    <div className="hero__footer">
      {/*
        aria-live: mientras las portadas rotan solas, un lector de pantalla no
        anuncia cada cambio (sería una interrupción constante). Si la persona
        pausó y cambia a mano, sí se anuncia.
      */}
      <div className="hero__project-region" aria-live={isPlaying ? 'off' : 'polite'}>
        {/* key: al cambiar de proyecto se repite el fundido de entrada */}
        <Link key={project.slug} to={`/proyectos/${project.slug}`} className="hero__project">
          {project.category && (
            <span className="hero__project-category">{project.category.name}</span>
          )}
          <span className="hero__project-title">
            {project.title} <span aria-hidden="true">→</span>
          </span>
        </Link>
      </div>

      {canRotate && (
        <div className="hero__controls">
          <div className="hero__buttons">
            <button
              type="button"
              className="hero__button"
              onClick={slideshow.previous}
              aria-label="Portada anterior"
            >
              <span aria-hidden="true">←</span>
            </button>
            <button
              type="button"
              className="hero__button"
              onClick={slideshow.toggle}
              aria-label={isPlaying ? 'Pausar la rotación' : 'Reanudar la rotación'}
            >
              <span aria-hidden="true">{isPlaying ? '❚❚' : '▶'}</span>
            </button>
            <button
              type="button"
              className="hero__button"
              onClick={slideshow.next}
              aria-label="Portada siguiente"
            >
              <span aria-hidden="true">→</span>
            </button>
          </div>

          <div className="hero__indicators">
            {slides.map((slide, position) => (
              <button
                key={slide.slug}
                type="button"
                className="hero__indicator"
                onClick={() => slideshow.goTo(position)}
                aria-label={`Ir a la portada ${position + 1} de ${slides.length}: ${slide.title}`}
                aria-current={position === index ? 'true' : undefined}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

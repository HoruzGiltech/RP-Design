import { Link } from 'react-router-dom'

/**
 * Parte inferior del hero: el proyecto que se está viendo (con su enlace) y,
 * si hay más de una portada, los controles.
 *
 * Los controles son discretos (specs-002, RF-15): una línea fina con una barra
 * por portada, dos flechas pequeñas y la pausa, sin recuadros. No se quitan:
 * lo que rota solo debe poder pararse y manejarse a mano.
 *
 * slides:    portadas del hero. Las de proyecto traen `project`; el video y la
 *            imagen de la Portada no, y por eso no muestran enlace.
 * slideshow: lo que devuelve useSlideshow
 */
export default function HeroControls({ slides, slideshow }) {
  const { index, isPlaying, isRunning, isTimed, canRotate } = slideshow
  const { project } = slides[index]
  // La barra solo avanza como reloj en las portadas que cambian por tiempo.
  // En el video se muestra llena y quieta: no se sabe cuánto dura.
  const showsProgress = isRunning && isTimed

  return (
    <div className="hero__footer">
      {/*
        aria-live: mientras las portadas rotan solas, un lector de pantalla no
        anuncia cada cambio (sería una interrupción constante). Si la persona
        pausó y cambia a mano, sí se anuncia.
      */}
      <div className="hero__project-region" aria-live={isPlaying ? 'off' : 'polite'}>
        {/* key: al cambiar de proyecto se repite el fundido de entrada */}
        {project && (
          <Link key={project.slug} to={`/proyectos/${project.slug}`} className="hero__project">
            {project.category && (
              <span className="hero__project-category">{project.category.name}</span>
            )}
            <span className="hero__project-title">
              {project.title} <span aria-hidden="true">→</span>
            </span>
          </Link>
        )}
      </div>

      {canRotate && (
        <div className="hero__controls">
          <button
            type="button"
            className="hero__control"
            onClick={slideshow.previous}
            aria-label="Portada anterior"
          >
            <span aria-hidden="true">‹</span>
          </button>

          <div className="hero__indicators">
            {slides.map((slide, position) => {
              const isActive = position === index
              return (
                <button
                  key={slide.key}
                  type="button"
                  className="hero__indicator"
                  onClick={() => slideshow.goTo(position)}
                  aria-label={`Ir a la portada ${position + 1} de ${slides.length}: ${slide.label}`}
                  aria-current={isActive ? 'true' : undefined}
                >
                  {/*
                    Relleno de la barra activa. Mientras la rotación corre, crece
                    como barra de progreso; en pausa (y en el video) se muestra
                    llena y quieta.
                    Al aparecer de nuevo, la animación empieza desde cero.
                  */}
                  {isActive && (
                    <span
                      className={
                        showsProgress ? 'hero__indicator-fill is-running' : 'hero__indicator-fill'
                      }
                    />
                  )}
                </button>
              )
            })}
          </div>

          <button
            type="button"
            className="hero__control"
            onClick={slideshow.next}
            aria-label="Portada siguiente"
          >
            <span aria-hidden="true">›</span>
          </button>
          <button
            type="button"
            className="hero__control hero__control--pause"
            onClick={slideshow.toggle}
            aria-label={isPlaying ? 'Pausar la rotación' : 'Reanudar la rotación'}
          >
            <span aria-hidden="true">{isPlaying ? '❚❚' : '▶'}</span>
          </button>
        </div>
      )}
    </div>
  )
}

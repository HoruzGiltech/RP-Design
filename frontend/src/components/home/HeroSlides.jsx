import { useEffect, useRef } from 'react'

/**
 * El video de la Portada como una portada más del hero (specs-003, RF-26).
 *
 * Se reproduce sin sonido mientras es la portada activa. Al terminar avisa
 * con onEnded para pasar a la siguiente; fuera de turno queda en pausa.
 *
 * shouldAdvance: false cuando la rotación está detenida (pausa, cursor encima)
 *                o cuando el video es la única portada. En ese caso, al
 *                terminar vuelve a empezar.
 */
function HeroVideoSlide({ slide, isActive, shouldAdvance, onEnded }) {
  const videoRef = useRef(null)

  useEffect(() => {
    const video = videoRef.current
    if (!isActive) {
      video.pause()
      return
    }
    // Cada vez que le toca, empieza desde el principio
    video.currentTime = 0
    // play() falla si el navegador no permite reproducir solo: queda la imagen de vista previa
    video.play().catch(() => {})
  }, [isActive])

  function handleEnded() {
    if (shouldAdvance) {
      onEnded()
      return
    }
    videoRef.current.currentTime = 0
    videoRef.current.play().catch(() => {})
  }

  return (
    <video
      ref={videoRef}
      className={isActive ? 'hero__slide hero__slide--video is-active' : 'hero__slide hero__slide--video'}
      src={slide.video}
      poster={slide.poster || undefined}
      aria-label={isActive ? slide.alt || undefined : undefined}
      aria-hidden={isActive ? undefined : 'true'}
      // Sin sonido: es la condición de los navegadores para reproducir un video solo
      muted
      playsInline
      preload="metadata"
      onEnded={handleEnded}
    />
  )
}

/**
 * Las portadas del hero, una encima de otra. Solo la activa es visible;
 * el cambio entre ellas es un fundido (ver motion.css).
 *
 * slides:        portadas del hero (las arma Hero.jsx): video, imagen o proyecto
 * index:         posición de la portada activa
 * previousIndex: posición de la que se está desvaneciendo
 * shouldAdvance: true si al terminar el video hay que pasar a la siguiente
 * onVideoEnded:  qué hacer cuando el video termina
 */
export default function HeroSlides({ slides, index, previousIndex, shouldAdvance, onVideoEnded }) {
  const nextIndex = (index + 1) % slides.length

  return slides.map((slide, position) => {
    const isActive = position === index
    // Solo se ponen en la página la portada activa, la que sale y la que viene.
    // Así las demás fotos grandes no se descargan hasta que les toca.
    const isNeeded = isActive || position === previousIndex || position === nextIndex
    if (!isNeeded) return null

    if (slide.type === 'video') {
      return (
        <HeroVideoSlide
          key={slide.key}
          slide={slide}
          isActive={isActive}
          shouldAdvance={shouldAdvance}
          onEnded={onVideoEnded}
        />
      )
    }

    return (
      <img
        key={slide.key}
        className={isActive ? 'hero__slide is-active' : 'hero__slide'}
        src={slide.image}
        // El texto alternativo solo se anuncia para la portada que se ve
        alt={isActive ? slide.alt : ''}
        aria-hidden={isActive ? undefined : 'true'}
        // La primera es lo más importante de la página: se carga con prioridad
        fetchPriority={position === 0 ? 'high' : 'low'}
      />
    )
  })
}

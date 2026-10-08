import { useEffect, useState } from 'react'

import { prefersReducedMotion } from './useReveal'

/**
 * Lleva la cuenta de qué portada se muestra en el hero y cuándo toca cambiar.
 *
 *   const slideshow = useSlideshow(slides.length, 6000)
 *
 * Devuelve:
 *   index          posición de la portada que se ve ahora
 *   previousIndex  posición de la que se veía antes (se está desvaneciendo)
 *   isPlaying      true si la rotación automática está activa (no la pausó la persona)
 *   isRunning      true si además está avanzando ahora mismo (sin cursor ni foco encima)
 *   canRotate      true si hay más de una portada
 *   next, previous, goTo(n)   para cambiar a mano
 *   toggle         pausa o reanuda (botón de pausa)
 *   hold(true|false)  pausa temporal mientras el cursor o el foco están encima
 *
 * La rotación se detiene sola cuando: hay una sola portada, la persona pulsó
 * pausa, el cursor o el foco están encima, o la pestaña no está a la vista.
 * Con "reducir movimiento" activo, arranca en pausa.
 */
export function useSlideshow(total, intervalMs) {
  const [position, setPosition] = useState({ index: 0, previousIndex: null })
  const [isPausedByUser, setIsPausedByUser] = useState(prefersReducedMotion)
  const [isHeld, setIsHeld] = useState(false)

  const canRotate = total > 1
  // Si el número de portadas baja, el índice guardado podría quedar fuera de rango
  const index = canRotate ? position.index % total : 0
  const isPlaying = canRotate && !isPausedByUser
  const isRunning = isPlaying && !isHeld

  function goTo(newIndex) {
    setPosition((current) => ({ index: newIndex, previousIndex: current.index }))
  }

  function next() {
    goTo((index + 1) % total)
  }

  function previous() {
    goTo((index - 1 + total) % total)
  }

  useEffect(() => {
    if (!isRunning) return undefined

    const timer = setInterval(() => {
      // Con la pestaña en segundo plano no se avanza: nadie lo está viendo
      if (document.visibilityState !== 'visible') return
      setPosition((current) => ({
        index: (current.index + 1) % total,
        previousIndex: current.index,
      }))
    }, intervalMs)

    return () => clearInterval(timer)
    // `index` está en la lista a propósito: cada cambio de portada (también a
    // mano) reinicia la cuenta, y así todas se ven el tiempo completo.
  }, [isRunning, total, intervalMs, index])

  return {
    index,
    previousIndex: position.previousIndex,
    isPlaying,
    isRunning,
    canRotate,
    next,
    previous,
    goTo,
    toggle: () => setIsPausedByUser((isPaused) => !isPaused),
    hold: setIsHeld,
  }
}

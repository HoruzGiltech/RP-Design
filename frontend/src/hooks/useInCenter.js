import { useEffect, useRef, useState } from 'react'

import { prefersReducedMotion } from './useReveal'

// Deja como zona de observación solo la línea horizontal del centro de la
// pantalla: se recorta el 50 % de arriba y el 50 % de abajo.
const CENTER_LINE = '-50% 0px -50% 0px'

/** ¿La pantalla es táctil, sin cursor que "pase por encima"? */
function isTouchScreen() {
  return window.matchMedia('(hover: none)').matches
}

/**
 * Dice si un elemento está cruzando el centro de la pantalla (specs-005, RF-46).
 *
 *   const { ref, isInCenter } = useInCenter()
 *   <div ref={ref} className={isInCenter ? 'is-centered' : ''}>
 *
 * Es el reemplazo de "pasar el cursor" en un celular: mientras se hace
 * scroll, la tarjeta que pasa por el centro muestra su capa y la oculta al
 * salir. Como se observa una línea, nunca hay dos tarjetas activas a la vez.
 *
 * A diferencia de useReveal, no se dispara una sola vez: el valor cambia cada
 * vez que el elemento entra o sale del centro.
 *
 * En pantallas con cursor no hace nada (devuelve siempre false).
 *
 * alwaysWhenReduced: qué devolver en táctil cuando el visitante pidió "reducir
 *   movimiento" (o el navegador no puede observar). true = siempre visible,
 *   para los textos que no se leen en ningún otro lugar.
 */
export function useInCenter({ alwaysWhenReduced = false } = {}) {
  const ref = useRef(null)
  const isTouch = isTouchScreen()
  const canObserve = isTouch && 'IntersectionObserver' in window && !prefersReducedMotion()
  const [isInCenter, setIsInCenter] = useState(false)

  useEffect(() => {
    const element = ref.current
    if (!canObserve || !element) return undefined

    const observer = new IntersectionObserver(
      ([entry]) => setIsInCenter(entry.isIntersecting),
      { rootMargin: CENTER_LINE },
    )
    observer.observe(element)

    return () => observer.disconnect()
  }, [canObserve])

  if (canObserve) return { ref, isInCenter }
  // Sin observador: fijo. En táctil depende de lo que pida quien usa el hook.
  return { ref, isInCenter: isTouch && alwaysWhenReduced }
}

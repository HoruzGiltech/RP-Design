import { useEffect, useRef, useState } from 'react'

/** ¿El visitante pidió a su sistema que reduzca las animaciones? */
export function prefersReducedMotion() {
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches
}

// La entrada empieza cuando el elemento ya subió un poco por la pantalla, no
// cuando apenas asoma por el borde de abajo: ahí la animación terminaba antes
// de que nadie la viera, sobre todo en un celular (specs-005, RF-47).
// Se consigue recortando el 12 % inferior de la zona que se observa.
const START_LINE = '0px 0px -12% 0px'

// Qué parte del elemento debe haber cruzado esa línea para considerarlo "a la vista"
const VISIBLE_RATIO = 0.1

/** ¿La página ya no baja más? */
function isAtPageEnd() {
  return window.scrollY + window.innerHeight >= document.documentElement.scrollHeight - 2
}

/**
 * Dice si un elemento está a la vista, para animar su entrada.
 *
 *   const { ref, isVisible } = useReveal()
 *   <div ref={ref} className={isVisible ? 'is-visible' : ''}>
 *
 * La entrada se repite: cada vez que el elemento sale de la pantalla vuelve a
 * su estado inicial, y al regresar se anima de nuevo (specs-008, RF-64).
 *
 * Si el navegador no puede observar el elemento, o el visitante prefiere
 * menos movimiento, `isVisible` vale true siempre: el contenido nunca se
 * queda oculto.
 */
export function useReveal() {
  const ref = useRef(null)
  const canAnimate = 'IntersectionObserver' in window && !prefersReducedMotion()
  const [isVisible, setIsVisible] = useState(!canAnimate)

  useEffect(() => {
    const element = ref.current
    if (!canAnimate || !element) return undefined

    // No se deja de observar al aparecer: así la animación se repite cada
    // vez que el elemento vuelve a entrar en pantalla.
    const observer = new IntersectionObserver(
      ([entry]) => setIsVisible(entry.intersectionRatio >= VISIBLE_RATIO),
      { rootMargin: START_LINE, threshold: VISIBLE_RATIO },
    )
    observer.observe(element)

    // Red de seguridad: lo que queda en la franja de abajo cuando la página ya
    // no baja más nunca cruzaría la línea de arranque. Al llegar al final de
    // la página se muestra, para que nada se quede oculto.
    function showAtPageEnd() {
      if (isAtPageEnd()) setIsVisible(true)
    }
    // passive: le avisa al navegador que este código no frena el scroll
    window.addEventListener('scroll', showAtPageEnd, { passive: true })
    // Una página tan corta que no tiene scroll ya está "al final"
    showAtPageEnd()

    return () => {
      observer.disconnect()
      window.removeEventListener('scroll', showAtPageEnd)
    }
  }, [canAnimate])

  return { ref, isVisible }
}

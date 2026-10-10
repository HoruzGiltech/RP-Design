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

/** ¿La página ya no baja más? */
function isAtPageEnd() {
  return window.scrollY + window.innerHeight >= document.documentElement.scrollHeight - 2
}

/**
 * Avisa cuando un elemento entra en pantalla, una sola vez.
 *
 *   const { ref, isVisible } = useReveal()
 *   <div ref={ref} className={isVisible ? 'is-visible' : ''}>
 *
 * Si el navegador no puede observar el elemento, o el visitante prefiere
 * menos movimiento, `isVisible` vale true desde el principio: el contenido
 * nunca se queda oculto.
 */
export function useReveal() {
  const ref = useRef(null)
  const canAnimate = 'IntersectionObserver' in window && !prefersReducedMotion()
  const [isVisible, setIsVisible] = useState(!canAnimate)

  useEffect(() => {
    const element = ref.current
    if (!canAnimate || !element) return undefined

    function show() {
      setIsVisible(true)
      // Ya apareció: se deja de vigilar para que la animación no se repita
      stopWatching()
    }

    // Red de seguridad: lo que queda en la franja de abajo cuando la página ya
    // no baja más nunca cruzaría la línea de arranque. Al llegar al final de
    // la página se muestra todo, para que nada se quede oculto.
    function showAtPageEnd() {
      if (isAtPageEnd()) show()
    }

    function stopWatching() {
      observer.disconnect()
      window.removeEventListener('scroll', showAtPageEnd)
    }

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) show()
      },
      // Se activa cuando el 10 % del elemento pasó la línea de arranque
      { rootMargin: START_LINE, threshold: 0.1 },
    )
    observer.observe(element)
    // passive: le avisa al navegador que este código no frena el scroll
    window.addEventListener('scroll', showAtPageEnd, { passive: true })
    // Una página tan corta que no tiene scroll ya está "al final"
    showAtPageEnd()

    return stopWatching
  }, [canAnimate])

  return { ref, isVisible }
}

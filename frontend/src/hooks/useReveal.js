import { useEffect, useRef, useState } from 'react'

/** ¿El visitante pidió a su sistema que reduzca las animaciones? */
export function prefersReducedMotion() {
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches
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

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true)
          // Ya apareció: se deja de observar para que la animación no se repita
          observer.disconnect()
        }
      },
      // Se activa cuando asoma el 15 % del elemento
      { threshold: 0.15 },
    )
    observer.observe(element)

    return () => observer.disconnect()
  }, [canAnimate])

  return { ref, isVisible }
}

import { useEffect, useState } from 'react'

// Movimientos más pequeños que esto se ignoran, para que el encabezado no parpadee
const MIN_SCROLL_DELTA = 8
// Cerca del inicio de la página el encabezado se muestra siempre
const TOP_ZONE = 96

/**
 * Dice si el encabezado debe ocultarse: se oculta mientras la persona baja
 * por la página y vuelve en cuanto sube un poco (specs-002, RF-13.5).
 *
 *   const isHidden = useHideOnScroll({ disabled: isMenuOpen })
 *
 * disabled: true para no ocultarlo nunca (por ejemplo, con el menú abierto).
 */
export function useHideOnScroll({ disabled = false } = {}) {
  const [isScrollingDown, setIsScrollingDown] = useState(false)

  useEffect(() => {
    let lastPosition = window.scrollY

    function handleScroll() {
      const position = window.scrollY
      const delta = position - lastPosition
      if (Math.abs(delta) < MIN_SCROLL_DELTA) return

      setIsScrollingDown(delta > 0 && position > TOP_ZONE)
      lastPosition = position
    }

    // passive: le avisa al navegador que este código no frena el scroll
    window.addEventListener('scroll', handleScroll, { passive: true })
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  return isScrollingDown && !disabled
}

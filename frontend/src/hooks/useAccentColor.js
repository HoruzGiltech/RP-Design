import { useEffect } from 'react'

/**
 * Aplica el color de acento que el cliente eligió en el panel.
 * Sobrescribe la variable --color-accent de tokens.css, y con eso cambian
 * los botones principales y los números de Servicios.
 */
export function useAccentColor(accentColor) {
  useEffect(() => {
    if (!accentColor) return
    document.documentElement.style.setProperty('--color-accent', accentColor)
  }, [accentColor])
}

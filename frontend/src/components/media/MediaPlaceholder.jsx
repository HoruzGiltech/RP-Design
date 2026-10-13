import './MediaPlaceholder.css'

/**
 * Recuadro liso que ocupa el lugar de una foto o un video cuando el cliente
 * todavía no subió nada. Evita que el diseño se rompa o quede un hueco.
 *
 * variant: "light" (sobre fondo claro) o "dark" (sobre fondo oscuro, y en la Portada)
 */
export default function MediaPlaceholder({ variant = 'light', className = '' }) {
  // aria-hidden: es un adorno, no hay nada que un lector de pantalla deba anunciar
  return (
    <div
      className={`media-placeholder media-placeholder--${variant} ${className}`}
      aria-hidden="true"
    />
  )
}

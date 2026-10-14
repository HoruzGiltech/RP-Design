import './Section.css'

/**
 * Bloque de sección del inicio: pone el fondo, el ancho máximo y el espacio
 * vertical de la maqueta.
 *
 * variant:    "light" (fondo general), "alt" (Contacto) o "dark" (Proyectos)
 * background: opcional, una imagen o un video que cubre toda la sección detrás
 *             del contenido, con una capa oscura encima (specs-009)
 */
export default function Section({ id, variant = 'light', className = '', background, children }) {
  const sectionClass = background
    ? `section section--${variant} section--with-background`
    : `section section--${variant}`

  return (
    <section id={id} className={sectionClass}>
      {background}
      <div className={`container section__inner ${className}`}>{children}</div>
    </section>
  )
}

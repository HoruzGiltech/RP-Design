import './Section.css'

/**
 * Bloque de sección del inicio: pone el fondo, el ancho máximo y el espacio
 * vertical de la maqueta.
 *
 * variant: "light" (fondo general), "alt" (Contacto) o "dark" (Proyectos)
 */
export default function Section({ id, variant = 'light', className = '', children }) {
  return (
    <section id={id} className={`section section--${variant}`}>
      <div className={`container section__inner ${className}`}>{children}</div>
    </section>
  )
}

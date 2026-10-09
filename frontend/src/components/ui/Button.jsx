import { Link } from 'react-router-dom'

import './Button.css'

/**
 * Botón del sitio. Según lo que reciba, se dibuja como:
 *   - <Link>   si tiene `to`   (navegación dentro del sitio, sin recargar)
 *   - <a>      si tiene `href` (enlace externo, como WhatsApp)
 *   - <button> en cualquier otro caso
 *
 * variant: "primary" (fondo de acento) o "secondary" (solo borde)
 * size:    "medium", "small" (el del encabezado) o "large" (el que invita a ver los proyectos)
 * onDark:  true cuando va sobre fondo oscuro
 */
export default function Button({
  variant = 'primary',
  size = 'medium',
  onDark = false,
  to,
  href,
  className = '',
  children,
  ...rest
}) {
  const classes = [
    'button',
    `button--${variant}`,
    `button--${size}`,
    onDark ? 'button--on-dark' : '',
    className,
  ]
    .filter(Boolean)
    .join(' ')

  if (to) {
    return (
      <Link to={to} className={classes} {...rest}>
        {children}
      </Link>
    )
  }
  if (href) {
    return (
      <a href={href} className={classes} {...rest}>
        {children}
      </a>
    )
  }
  return (
    <button type="button" className={classes} {...rest}>
      {children}
    </button>
  )
}

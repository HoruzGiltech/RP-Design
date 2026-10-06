import { useReveal } from '../../hooks/useReveal'

/**
 * Hace que su contenido aparezca con un fundido y un pequeño desplazamiento
 * cuando entra en pantalla (specs/design.md §3.6). La animación está en
 * styles/motion.css.
 *
 * as:    etiqueta HTML a usar ("div", "h2", "li", "article"...)
 * from:  desde dónde entra: "bottom", "left" o "right"
 * index: posición dentro de un grupo; cada elemento espera un poco más que el anterior
 */
export default function Reveal({
  as: Tag = 'div',
  from = 'bottom',
  index = 0,
  className = '',
  style,
  children,
  ...rest
}) {
  const { ref, isVisible } = useReveal()

  const classes = ['reveal', `reveal--from-${from}`, isVisible ? 'is-visible' : '', className]
    .filter(Boolean)
    .join(' ')

  return (
    <Tag ref={ref} className={classes} style={{ '--reveal-index': index, ...style }} {...rest}>
      {children}
    </Tag>
  )
}

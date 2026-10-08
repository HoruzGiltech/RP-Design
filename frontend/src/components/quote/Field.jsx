/**
 * Un campo del formulario: etiqueta, control y mensaje de error.
 *
 * as:       "input" (por defecto), "select" o "textarea"
 * name:     nombre del campo; también se usa para armar los id
 * label:    texto de la etiqueta
 * error:    mensaje de error del campo, si lo hay
 * hint:     ayuda breve bajo la etiqueta (opcional)
 * className: clase extra para el contenedor (por ejemplo, para colocarlo en la grilla)
 * children: las <option> cuando es un select
 * El resto de propiedades (value, onChange, type, placeholder...) va al control.
 */
export default function Field({
  as: Control = 'input',
  name,
  label,
  error,
  hint,
  className = '',
  children,
  ...controlProps
}) {
  const id = `quote-${name}`
  const errorId = `${id}-error`
  const hintId = `${id}-hint`

  // aria-describedby une el control con su ayuda y su error:
  // un lector de pantalla los lee al entrar al campo.
  const describedBy = [hint ? hintId : null, error ? errorId : null].filter(Boolean).join(' ')

  return (
    <div className={`quote-field ${className}`}>
      <label className="quote-field__label" htmlFor={id}>
        {label}
      </label>
      {hint && (
        <span className="quote-field__hint" id={hintId}>
          {hint}
        </span>
      )}
      <Control
        className="quote-field__control"
        id={id}
        name={name}
        aria-invalid={error ? 'true' : undefined}
        aria-describedby={describedBy || undefined}
        {...controlProps}
      >
        {children}
      </Control>
      {error && (
        <span className="quote-field__error" id={errorId}>
          {error}
        </span>
      )}
    </div>
  )
}

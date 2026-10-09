/**
 * Una casilla del formulario con su texto al lado y, si lo hay, su error.
 *
 * id:       identificador único en la página
 * name:     nombre del campo (lo usa el manejador del formulario)
 * checked:  si está marcada
 * onChange: se llama al marcarla o desmarcarla
 * error:    mensaje de error, si lo hay
 * className: clase extra para el contenedor (por ejemplo, para colocarlo en la grilla)
 * children: el texto de la casilla (puede llevar un enlace)
 */
export default function CheckboxField({
  id,
  name,
  checked,
  onChange,
  error,
  className = '',
  children,
}) {
  const errorId = `${id}-error`

  return (
    <div className={`quote-check ${className}`}>
      <input
        className="quote-check__box"
        id={id}
        name={name}
        type="checkbox"
        checked={checked}
        onChange={onChange}
        aria-invalid={error ? 'true' : undefined}
        aria-describedby={error ? errorId : undefined}
      />
      <label className="quote-check__label" htmlFor={id}>
        {children}
      </label>
      {error && (
        <span className="quote-field__error quote-check__error" id={errorId}>
          {error}
        </span>
      )}
    </div>
  )
}

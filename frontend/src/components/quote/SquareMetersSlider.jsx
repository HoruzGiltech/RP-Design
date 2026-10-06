const MIN_SQUARE_METERS = 1
const STEP = 1

/**
 * Control deslizante para elegir los metros cuadrados.
 *
 * Es un <input type="range"> del navegador: ya funciona con el dedo, con el
 * mouse y con las flechas del teclado. Aquí solo se le da el aspecto del sitio.
 *
 * value:    metros cuadrados elegidos (texto, como todos los campos del formulario)
 * max:      tope del control; es el "máximo de m²" configurado en el panel
 * onChange: el mismo manejador del resto del formulario
 * error:    mensaje de error del campo, si lo hay
 */
export default function SquareMetersSlider({ value, max, onChange, error }) {
  const maximum = Math.floor(Number(max))
  // Qué parte de la línea queda "llena", de 0 a 100. La usa el CSS para pintarla.
  const filledPercent = ((Number(value) - MIN_SQUARE_METERS) / (maximum - MIN_SQUARE_METERS)) * 100

  return (
    <div className="quote-field quote-slider">
      <div className="quote-slider__header">
        <label className="quote-field__label" htmlFor="quote-square_meters">
          Metros cuadrados
        </label>
        {/* Adorno visual: el valor ya lo anuncia el propio control (aria-valuetext) */}
        <span className="quote-slider__value" aria-hidden="true">
          {value} m²
        </span>
      </div>

      <input
        className="quote-slider__input"
        id="quote-square_meters"
        name="square_meters"
        type="range"
        min={MIN_SQUARE_METERS}
        max={maximum}
        step={STEP}
        value={value}
        onChange={onChange}
        style={{ '--slider-filled': `${filledPercent}%` }}
        // Lo que lee un lector de pantalla: "25 metros cuadrados" y no solo "25"
        aria-valuetext={`${value} metros cuadrados`}
        aria-invalid={error ? 'true' : undefined}
        aria-describedby={error ? 'quote-square_meters-error' : undefined}
      />

      <div className="quote-slider__range" aria-hidden="true">
        <span>{MIN_SQUARE_METERS} m²</span>
        <span>{maximum} m²</span>
      </div>

      {error && (
        <span className="quote-field__error" id="quote-square_meters-error">
          {error}
        </span>
      )}
    </div>
  )
}

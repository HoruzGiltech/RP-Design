import { parseDecimal } from '../../utils/estimate'

const MIN_SQUARE_METERS = 1
const STEP = 1

/**
 * Dónde va el botón de la barra para lo que hay escrito en el campo.
 * La barra va de metro en metro y entre el mínimo y el máximo: "12,5" la deja
 * en 13, y un texto que no es un número, en el mínimo.
 */
function getSliderPosition(value, maximum) {
  const number = parseDecimal(value)
  if (number === null) return MIN_SQUARE_METERS
  return Math.min(Math.max(Math.round(number), MIN_SQUARE_METERS), maximum)
}

/**
 * Metros cuadrados de un área: un campo para escribirlos y una barra para
 * deslizarlos. Los dos muestran el mismo valor (specs-003, RF-29): escribir
 * mueve la barra, y mover la barra cambia el número.
 *
 * La barra es un <input type="range"> del navegador: ya funciona con el dedo,
 * con el mouse y con las flechas del teclado.
 *
 * id:       identificador del campo de texto (el de la barra se arma a partir de él)
 * label:    título del campo, editable desde el panel
 * areaName: nombre del área, para que un lector de pantalla diga de cuál son los metros
 * value:    lo que hay escrito (texto, como todos los campos del formulario)
 * max:      tope; es el "máximo de m²" configurado en el panel
 * onChange: recibe el texto nuevo
 * error:    mensaje de error del campo, si lo hay
 */
export default function SquareMetersSlider({ id, label, areaName, value, max, onChange, error }) {
  const maximum = Math.floor(Number(max))
  const position = getSliderPosition(value, maximum)
  // Qué parte de la línea queda "llena", de 0 a 100. La usa el CSS para pintarla.
  const filledPercent = ((position - MIN_SQUARE_METERS) / (maximum - MIN_SQUARE_METERS)) * 100
  const errorId = `${id}-error`

  return (
    <div className="quote-field quote-slider">
      <div className="quote-slider__header">
        <label className="quote-field__label" htmlFor={id}>
          {label}
          <span className="visually-hidden"> de {areaName}</span>
        </label>
        <span className="quote-slider__number">
          <input
            className="quote-field__control quote-slider__text"
            id={id}
            // type="text" y no "number": así se puede escribir la coma decimal (12,5).
            // inputMode abre el teclado numérico en el celular.
            type="text"
            inputMode="decimal"
            autoComplete="off"
            value={value}
            onChange={(event) => onChange(event.target.value)}
            aria-invalid={error ? 'true' : undefined}
            aria-describedby={error ? errorId : undefined}
          />
          <span aria-hidden="true">m²</span>
        </span>
      </div>

      <input
        className="quote-slider__input"
        type="range"
        min={MIN_SQUARE_METERS}
        max={maximum}
        step={STEP}
        value={position}
        onChange={(event) => onChange(event.target.value)}
        style={{ '--slider-filled': `${filledPercent}%` }}
        aria-label={`${label} de ${areaName}, barra deslizante`}
        // Lo que lee un lector de pantalla: "25 metros cuadrados" y no solo "25"
        aria-valuetext={`${position} metros cuadrados`}
      />

      <div className="quote-slider__range" aria-hidden="true">
        <span>{MIN_SQUARE_METERS} m²</span>
        <span>{maximum} m²</span>
      </div>

      {error && (
        <span className="quote-field__error" id={errorId}>
          {error}
        </span>
      )}
    </div>
  )
}

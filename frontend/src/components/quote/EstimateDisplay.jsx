import { formatUSD, TO_BE_QUOTED } from '../../utils/currency'
import { calculateEstimate, calculateTotal, parseDecimal } from '../../utils/estimate'

const WAITING = '—'

/**
 * Estimado en vivo de la calculadora: la suma de todas las áreas marcadas
 * (specs-003, RF-27).
 *
 * selectedItems: las áreas marcadas, como [{ area, item }]. `area` es el objeto
 *                de la API e `item` lo que la persona llenó ({ square_meters })
 * needsVisit:    true si marcó "no sé cuántos m² son": no hay nada que calcular
 * note:          nota de precio editable desde el panel
 */
export default function EstimateDisplay({ selectedItems, needsVisit, note }) {
  const amount = getAmountText(selectedItems, needsVisit)

  return (
    <div className="quote-estimate">
      <span className="quote-estimate__label">Estimado</span>
      {/* aria-live: un lector de pantalla anuncia el monto cada vez que cambia */}
      <output className="quote-estimate__amount" aria-live="polite">
        {amount}
      </output>
      {note && <p className="quote-estimate__note">{note}</p>}
    </div>
  )
}

function getAmountText(selectedItems, needsVisit) {
  // Todavía no se eligió ningún área
  if (selectedItems.length === 0) return WAITING
  // Sin metros no hay cuenta: el precio se define en la visita
  if (needsVisit) return TO_BE_QUOTED

  const squareMeters = selectedItems.map(({ item }) => parseDecimal(item.square_meters))
  // Mientras algún área no tenga sus metros bien escritos, no se muestra una suma a medias
  if (squareMeters.some((meters) => meters === null || meters <= 0)) return WAITING

  const subtotals = selectedItems.map(({ area }, position) =>
    calculateEstimate(area.price_per_m2, squareMeters[position]),
  )
  // Si un área no tiene precio, calculateTotal devuelve null y formatUSD dice "A cotizar"
  return formatUSD(calculateTotal(subtotals))
}

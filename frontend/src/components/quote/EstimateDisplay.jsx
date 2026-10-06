import { formatUSD } from '../../utils/currency'
import { calculateEstimate } from '../../utils/estimate'

const WAITING = '—'

/**
 * Estimado en vivo de la calculadora.
 *
 * area:         el área elegida (objeto de la API) o undefined si aún no se eligió
 * squareMeters: metros cuadrados como número, o null si aún no son válidos
 * note:         nota de precio editable desde el panel
 */
export default function EstimateDisplay({ area, squareMeters, note }) {
  const amount = getAmountText(area, squareMeters)

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

function getAmountText(area, squareMeters) {
  // Todavía faltan datos para calcular
  if (!area || squareMeters === null || squareMeters <= 0) return WAITING
  // Si el área no tiene precio (o es "Otro"), calculateEstimate devuelve null
  // y formatUSD lo muestra como "A cotizar"
  return formatUSD(calculateEstimate(area.price_per_m2, squareMeters))
}

// Cálculo del estimado para mostrarlo en vivo mientras la persona escribe.
// Es solo una vista previa: el precio que vale es el que calcula el backend.

const DECIMAL_PATTERN = /^\d+([.,]\d{1,2})?$/

/**
 * Convierte lo que la persona escribió en un número.
 * Acepta coma o punto como decimal: "12,5" y "12.5" -> 12.5
 * Devuelve null si no es un número válido (o tiene más de 2 decimales).
 */
export function parseDecimal(text) {
  const trimmed = String(text).trim()
  if (!DECIMAL_PATTERN.test(trimmed)) return null
  return Number(trimmed.replace(',', '.'))
}

/** 12.5 -> 1250. Trabajar con centésimas enteras evita errores como 0.1 + 0.2. */
function toHundredths(number) {
  return Math.round(number * 100)
}

/**
 * Redondea al centavo como lo hace el backend: si queda justo en la mitad,
 * va al número par más cercano.
 */
function roundToCents(tenThousandths) {
  let cents = Math.floor(tenThousandths / 100)
  const remainder = tenThousandths % 100
  const isHalf = remainder === 50
  if (remainder > 50 || (isHalf && cents % 2 === 1)) cents += 1
  return cents
}

/**
 * m² × precio por m². Devuelve null si el área no tiene precio ("A cotizar").
 *
 * pricePerM2:   precio del área tal como llega de la API ("100.00") o null
 * squareMeters: número de metros cuadrados
 */
export function calculateEstimate(pricePerM2, squareMeters) {
  if (pricePerM2 === null || pricePerM2 === undefined || pricePerM2 === '') return null

  const product = toHundredths(Number(pricePerM2)) * toHundredths(squareMeters)
  return roundToCents(product) / 100
}

/**
 * Suma los subtotales de todas las áreas marcadas.
 *
 * Si alguna está "A cotizar" (null), el total también lo está: mostrar una
 * suma parcial haría creer que ese es el precio de todo. Es la misma regla
 * que calculate_total() del backend.
 */
export function calculateTotal(subtotals) {
  if (subtotals.length === 0 || subtotals.includes(null)) return null

  // Se suma en centavos enteros para no arrastrar errores de decimales
  const cents = subtotals.reduce((sum, subtotal) => sum + toHundredths(subtotal), 0)
  return cents / 100
}

// Formato de precios. Debe dar el mismo resultado que format_usd() del
// backend (backend/quotes/services.py).

export const TO_BE_QUOTED = 'A cotizar'

/**
 * 1250.5 -> "USD 1.250,50"   (punto para miles y coma para decimales)
 * null   -> "A cotizar"
 */
export function formatUSD(amount) {
  if (amount === null || amount === undefined) return TO_BE_QUOTED

  const [integerPart, decimalPart] = Number(amount).toFixed(2).split('.')
  // Pone un punto cada tres cifras, contando desde la derecha
  const withThousands = integerPart.replace(/\B(?=(\d{3})+(?!\d))/g, '.')
  return `USD ${withThousands},${decimalPart}`
}

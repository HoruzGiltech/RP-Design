// Números escritos por una persona en un formulario.

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

/**
 * Deja solo lo que puede formar un número: cifras, coma y punto.
 * Se usa mientras la persona escribe, para que un campo numérico no acepte letras.
 *
 * "45 m2" -> "452"   "12,5" -> "12,5"   "abc" -> ""
 */
export function keepNumberCharacters(text) {
  return String(text).replace(/[^\d.,]/g, '')
}

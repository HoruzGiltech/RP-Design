// Validación del formulario de cotización en el navegador.
// Sirve para avisar rápido de un error; la validación que manda es la del
// backend (backend/quotes/serializers.py), que repite estas mismas reglas.

import { parseDecimal } from './estimate'

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
const MIN_PHONE_DIGITS = 7
const MAX_PHONE_DIGITS = 15
export const MAX_MESSAGE_LENGTH = 1000

function countDigits(text) {
  return text.replace(/\D/g, '').length
}

/** 10000 -> "10.000". El máximo se muestra como lo escribe la gente. */
function formatMaximum(number) {
  return String(number).replace(/\B(?=(\d{3})+(?!\d))/g, '.')
}

/**
 * Nombre de un campo que pertenece a un área: (4, 'square_meters') -> "item_4_square_meters".
 * Con ese nombre se guarda su error y se arma el id del campo en la página.
 */
export function getItemFieldName(areaId, field) {
  return `item_${areaId}_${field}`
}

/** Mensaje de error de unos metros cuadrados, o null si están bien. */
function checkSquareMeters(text, maximum) {
  const squareMeters = parseDecimal(text)
  if (!text.trim()) return 'Escribe los metros cuadrados.'
  if (squareMeters === null) {
    return 'Escribe solo números, con dos decimales como máximo. Ejemplo: 12,5'
  }
  if (squareMeters <= 0) return 'Los metros cuadrados deben ser mayores que 0.'
  if (squareMeters > maximum) return `El máximo es ${formatMaximum(maximum)} m².`
  return null
}

/**
 * Revisa los valores del formulario.
 *
 * values:           { name, phone, email, category, location, items, needs_visit,
 *                     has_photos, message, privacy_accepted }
 *                   `items` tiene una entrada por cada área marcada:
 *                   { [id del área]: { square_meters, area_other } }
 * selectedCategory: el tipo de remodelación elegido (objeto de la API, con sus
 *                   áreas) o undefined
 * maxSquareMeters:  máximo de m² configurado en el panel
 *
 * Devuelve un objeto con un mensaje por cada campo con error.
 * Si está vacío, el formulario es válido.
 */
export function validateQuote(values, selectedCategory, maxSquareMeters) {
  const errors = {}

  if (!values.name.trim()) {
    errors.name = 'Escribe tu nombre.'
  }

  const phoneDigits = countDigits(values.phone)
  if (!values.phone.trim()) {
    errors.phone = 'Escribe tu teléfono.'
  } else if (phoneDigits < MIN_PHONE_DIGITS || phoneDigits > MAX_PHONE_DIGITS) {
    errors.phone = 'Escribe un número de teléfono válido.'
  }

  if (!values.email.trim()) {
    errors.email = 'Escribe tu correo.'
  } else if (!EMAIL_PATTERN.test(values.email.trim())) {
    errors.email = 'Escribe un correo válido, como nombre@correo.com.'
  }

  if (!selectedCategory) {
    errors.category = 'Elige el tipo de remodelación.'
  }

  // Solo cuentan las áreas del tipo elegido que estén marcadas
  const areas = selectedCategory ? selectedCategory.areas : []
  const selectedAreas = areas.filter((area) => values.items[area.id])
  if (selectedCategory && selectedAreas.length === 0) {
    errors.items = 'Elige al menos un área.'
  }

  const maximum = Number(maxSquareMeters)
  for (const area of selectedAreas) {
    const item = values.items[area.id]

    if (area.is_other && !item.area_other.trim()) {
      errors[getItemFieldName(area.id, 'area_other')] = 'Especifica qué área quieres remodelar.'
    }
    // Quien pide una visita no sabe los metros: no se le exigen
    if (!values.needs_visit) {
      const metersError = checkSquareMeters(item.square_meters, maximum)
      if (metersError) errors[getItemFieldName(area.id, 'square_meters')] = metersError
    }
  }

  if (values.message.length > MAX_MESSAGE_LENGTH) {
    errors.message = `El mensaje no puede pasar de ${formatMaximum(MAX_MESSAGE_LENGTH)} caracteres.`
  }

  if (!values.privacy_accepted) {
    errors.privacy_accepted = 'Debes aceptar la política de privacidad.'
  }

  return errors
}

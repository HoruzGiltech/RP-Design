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
 * Revisa los valores del formulario.
 *
 * values:           { name, phone, email, area, area_other, square_meters, message }
 * selectedArea:     el área elegida (objeto de la API) o undefined
 * maxSquareMeters:  máximo de m² configurado en el panel
 *
 * Devuelve un objeto con un mensaje por cada campo con error.
 * Si está vacío, el formulario es válido.
 */
export function validateQuote(values, selectedArea, maxSquareMeters) {
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

  if (!selectedArea) {
    errors.area = 'Elige el área a remodelar.'
  } else if (selectedArea.is_other && !values.area_other.trim()) {
    errors.area_other = 'Especifica qué área quieres remodelar.'
  }

  const squareMeters = parseDecimal(values.square_meters)
  const maximum = Number(maxSquareMeters)
  if (!values.square_meters.trim()) {
    errors.square_meters = 'Escribe los metros cuadrados.'
  } else if (squareMeters === null) {
    errors.square_meters = 'Escribe solo números, con dos decimales como máximo. Ejemplo: 12,5'
  } else if (squareMeters <= 0) {
    errors.square_meters = 'Los metros cuadrados deben ser mayores que 0.'
  } else if (squareMeters > maximum) {
    errors.square_meters = `El máximo es ${formatMaximum(maximum)} m².`
  }

  if (values.message.length > MAX_MESSAGE_LENGTH) {
    errors.message = `El mensaje no puede pasar de ${formatMaximum(MAX_MESSAGE_LENGTH)} caracteres.`
  }

  return errors
}

// Validación del formulario de cotización en el navegador.
// Sirve para avisar rápido de un error; la validación que manda es la del
// backend (backend/quotes/serializers.py), que repite estas mismas reglas.

import { parseDecimal } from './numbers'

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
const MIN_PHONE_DIGITS = 7
const MAX_PHONE_DIGITS = 15
export const MAX_MESSAGE_LENGTH = 1000

function countDigits(text) {
  return text.replace(/\D/g, '').length
}

/**
 * Revisa los valores del formulario (specs-008).
 *
 * values: { name, phone, email, remodel_type, location, square_meters,
 *           needs_visit, has_photos, message, privacy_accepted }
 *
 * Devuelve un objeto con un mensaje por cada campo con error.
 * Si está vacío, el formulario es válido.
 */
export function validateQuote(values) {
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

  if (!values.remodel_type.trim()) {
    errors.remodel_type = 'Escribe qué quieres remodelar.'
  }

  if (!values.location.trim()) {
    errors.location = 'Escribe la ubicación del espacio.'
  }

  // Los metros son opcionales. Solo se revisan si la persona escribió algo y
  // no marcó que prefiere una visita (en ese caso el campo se ignora).
  const wroteSquareMeters = values.square_meters.trim() !== ''
  if (wroteSquareMeters && !values.needs_visit) {
    const squareMeters = parseDecimal(values.square_meters)
    if (squareMeters === null) {
      errors.square_meters = 'Escribe solo números, con dos decimales como máximo. Ejemplo: 12,5'
    } else if (squareMeters <= 0) {
      errors.square_meters = 'Los metros cuadrados deben ser mayores que 0.'
    }
  }

  if (values.message.length > MAX_MESSAGE_LENGTH) {
    errors.message = 'El mensaje no puede pasar de 1.000 caracteres.'
  }

  if (!values.privacy_accepted) {
    errors.privacy_accepted = 'Debes aceptar la política de privacidad.'
  }

  return errors
}

import { describe, expect, it } from 'vitest'

import { getItemFieldName, validateQuote } from './quoteValidation'

const KITCHEN = { id: 2, name: 'Cocina', price_per_m2: '100.00', is_other: false }
const LIVING_ROOM = { id: 3, name: 'Sala', price_per_m2: '50.00', is_other: false }
const OTHER = { id: 6, name: 'Otro', price_per_m2: null, is_other: true }
const RESIDENTIAL = {
  id: 1,
  name: 'Residencial',
  slug: 'residencial',
  areas: [KITCHEN, LIVING_ROOM, OTHER],
}
const MAX_SQUARE_METERS = '10000.00'

const KITCHEN_METERS = getItemFieldName(KITCHEN.id, 'square_meters')
const LIVING_ROOM_METERS = getItemFieldName(LIVING_ROOM.id, 'square_meters')
const OTHER_TEXT = getItemFieldName(OTHER.id, 'area_other')

/** Lo que la persona llena para un área marcada. */
function item(squareMeters = '12,5', areaOther = '') {
  return { square_meters: squareMeters, area_other: areaOther }
}

function validValues(changes = {}) {
  return {
    name: 'Ana Pérez',
    phone: '+58 412-1234567',
    email: 'ana@mail.com',
    category: '1',
    location: '',
    // Por defecto, solo la cocina marcada
    items: { [KITCHEN.id]: item() },
    needs_visit: false,
    has_photos: false,
    message: '',
    privacy_accepted: true,
    ...changes,
  }
}

function validate(changes) {
  return validateQuote(validValues(changes), RESIDENTIAL, MAX_SQUARE_METERS)
}

describe('validateQuote', () => {
  it('no devuelve errores con datos válidos', () => {
    expect(validate()).toEqual({})
  })

  it('pide los campos obligatorios', () => {
    const errors = validate({ name: ' ', phone: '', email: '', items: {} })

    expect(Object.keys(errors).sort()).toEqual(['email', 'items', 'name', 'phone'])
  })

  it('pide el tipo de remodelación', () => {
    const errors = validateQuote(validValues(), undefined, MAX_SQUARE_METERS)

    expect(errors.category).toContain('tipo de remodelación')
    // Sin tipo no hay áreas que ofrecer: no se reclama también por ellas
    expect(errors.items).toBeUndefined()
  })

  it('los campos nuevos son opcionales', () => {
    expect(validate({ location: '', has_photos: false, needs_visit: false, message: '' })).toEqual(
      {},
    )
  })

  it('rechaza un correo mal escrito', () => {
    expect(validate({ email: 'ana@mail' }).email).toContain('correo válido')
  })

  it('rechaza un teléfono demasiado corto o demasiado largo', () => {
    expect(validate({ phone: '123' }).phone).toContain('teléfono válido')
    expect(validate({ phone: '1234567890123456' }).phone).toContain('teléfono válido')
  })

  it('exige aceptar la política de privacidad', () => {
    expect(validate({ privacy_accepted: false }).privacy_accepted).toContain(
      'política de privacidad',
    )
  })

  it('el mensaje no puede pasar de 1000 caracteres', () => {
    expect(validate({ message: 'a'.repeat(1000) })).toEqual({})
    expect(validate({ message: 'a'.repeat(1001) }).message).toContain('1.000 caracteres')
  })
})

describe('validateQuote: áreas', () => {
  it('pide al menos un área', () => {
    expect(validate({ items: {} }).items).toBe('Elige al menos un área.')
  })

  it('acepta varias áreas, cada una con sus metros', () => {
    const items = { [KITCHEN.id]: item('10'), [LIVING_ROOM.id]: item('8,5') }

    expect(validate({ items })).toEqual({})
  })

  it('el error de metros es del área que lo tiene, no de las demás', () => {
    const items = { [KITCHEN.id]: item('10'), [LIVING_ROOM.id]: item('0') }

    const errors = validate({ items })

    expect(errors[LIVING_ROOM_METERS]).toContain('mayores que 0')
    expect(errors[KITCHEN_METERS]).toBeUndefined()
  })

  it('los metros cuadrados deben ser un número mayor que 0', () => {
    const errorFor = (text) => validate({ items: { [KITCHEN.id]: item(text) } })[KITCHEN_METERS]

    expect(errorFor('')).toContain('Escribe los metros')
    expect(errorFor('doce')).toContain('solo números')
    expect(errorFor('0')).toContain('mayores que 0')
  })

  it('los metros cuadrados no pueden pasar del máximo del panel', () => {
    expect(validate({ items: { [KITCHEN.id]: item('10000') } })).toEqual({})
    expect(validate({ items: { [KITCHEN.id]: item('10001') } })[KITCHEN_METERS]).toBe(
      'El máximo es 10.000 m².',
    )
  })

  it('pide especificar el área solo cuando se marca "Otro"', () => {
    expect(validate({ items: { [OTHER.id]: item('8', ' ') } })[OTHER_TEXT]).toContain('Especifica')
    expect(validate({ items: { [OTHER.id]: item('8', 'Terraza') } })).toEqual({})
    expect(validate({ items: { [KITCHEN.id]: item('8', '') } })).toEqual({})
  })

  it('con la visita marcada no se piden los metros', () => {
    const items = { [KITCHEN.id]: item(''), [LIVING_ROOM.id]: item('doce') }

    expect(validate({ needs_visit: true, items })).toEqual({})
  })

  it('con la visita marcada se sigue pidiendo el área y el texto de "Otro"', () => {
    expect(validate({ needs_visit: true, items: {} }).items).toBe('Elige al menos un área.')
    expect(validate({ needs_visit: true, items: { [OTHER.id]: item('', '') } })[OTHER_TEXT]).toContain(
      'Especifica',
    )
  })

  it('ignora un área marcada que no es del tipo elegido', () => {
    // Puede quedar una entrada vieja si el tipo cambió: no cuenta como área elegida
    expect(validate({ items: { 999: item('10') } }).items).toBe('Elige al menos un área.')
  })
})

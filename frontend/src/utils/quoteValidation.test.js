import { describe, expect, it } from 'vitest'

import { validateQuote } from './quoteValidation'

const KITCHEN = { id: 2, name: 'Cocina', price_per_m2: '100.00', is_other: false }
const OTHER = { id: 6, name: 'Otro', price_per_m2: null, is_other: true }
const MAX_SQUARE_METERS = '10000.00'

function validValues(changes = {}) {
  return {
    name: 'Ana Pérez',
    phone: '+58 412-1234567',
    email: 'ana@mail.com',
    area: '2',
    area_other: '',
    square_meters: '12,5',
    message: '',
    ...changes,
  }
}

function validate(changes, area = KITCHEN) {
  return validateQuote(validValues(changes), area, MAX_SQUARE_METERS)
}

describe('validateQuote', () => {
  it('no devuelve errores con datos válidos', () => {
    expect(validate()).toEqual({})
  })

  it('pide los campos obligatorios', () => {
    const errors = validateQuote(
      validValues({ name: ' ', phone: '', email: '', square_meters: '' }),
      undefined,
      MAX_SQUARE_METERS,
    )

    expect(Object.keys(errors).sort()).toEqual(['area', 'email', 'name', 'phone', 'square_meters'])
  })

  it('el mensaje es opcional', () => {
    expect(validate({ message: '' })).toEqual({})
  })

  it('rechaza un correo mal escrito', () => {
    expect(validate({ email: 'ana@mail' }).email).toContain('correo válido')
  })

  it('rechaza un teléfono demasiado corto o demasiado largo', () => {
    expect(validate({ phone: '123' }).phone).toContain('teléfono válido')
    expect(validate({ phone: '1234567890123456' }).phone).toContain('teléfono válido')
  })

  it('pide especificar el área solo cuando se elige "Otro"', () => {
    expect(validate({ area_other: '' }, OTHER).area_other).toContain('Especifica')
    expect(validate({ area_other: 'Terraza' }, OTHER)).toEqual({})
    expect(validate({ area_other: '' }, KITCHEN)).toEqual({})
  })

  it('los metros cuadrados deben ser un número mayor que 0', () => {
    expect(validate({ square_meters: 'doce' }).square_meters).toContain('solo números')
    expect(validate({ square_meters: '0' }).square_meters).toContain('mayores que 0')
  })

  it('los metros cuadrados no pueden pasar del máximo del panel', () => {
    expect(validate({ square_meters: '10000' })).toEqual({})
    expect(validate({ square_meters: '10001' }).square_meters).toBe('El máximo es 10.000 m².')
  })

  it('el mensaje no puede pasar de 1000 caracteres', () => {
    expect(validate({ message: 'a'.repeat(1000) })).toEqual({})
    expect(validate({ message: 'a'.repeat(1001) }).message).toContain('1.000 caracteres')
  })
})

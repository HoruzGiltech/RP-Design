import { describe, expect, it } from 'vitest'

import { validateQuote } from './quoteValidation'

function validate(changes = {}) {
  return validateQuote({
    name: 'Ana Pérez',
    phone: '+58 412-1234567',
    email: 'ana@mail.com',
    remodel_type: 'cocina y baño',
    location: 'Chacao, Caracas',
    square_meters: '45,5',
    needs_visit: false,
    has_photos: false,
    message: '',
    privacy_accepted: true,
    ...changes,
  })
}

describe('validateQuote', () => {
  it('no devuelve errores con datos válidos', () => {
    expect(validate()).toEqual({})
  })

  it('pide los campos obligatorios', () => {
    const errors = validate({ name: ' ', phone: '', email: '', remodel_type: ' ', location: '' })

    expect(Object.keys(errors).sort()).toEqual([
      'email',
      'location',
      'name',
      'phone',
      'remodel_type',
    ])
  })

  it('el tipo de remodelación es un texto libre obligatorio', () => {
    expect(validate({ remodel_type: '' }).remodel_type).toContain('qué quieres remodelar')
    expect(validate({ remodel_type: 'una quinta completa' })).toEqual({})
  })

  it('las casillas y el mensaje son opcionales', () => {
    expect(validate({ has_photos: false, needs_visit: false, message: '' })).toEqual({})
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

describe('validateQuote: metros cuadrados', () => {
  it('son opcionales', () => {
    expect(validate({ square_meters: '' })).toEqual({})
    expect(validate({ square_meters: '   ' })).toEqual({})
  })

  it('si se escriben, deben ser un número mayor que 0', () => {
    expect(validate({ square_meters: 'doce' }).square_meters).toContain('solo números')
    expect(validate({ square_meters: '0' }).square_meters).toContain('mayores que 0')
    expect(validate({ square_meters: '12.5' })).toEqual({})
  })

  it('con la visita marcada no se revisan', () => {
    expect(validate({ needs_visit: true, square_meters: 'no sé' })).toEqual({})
  })
})

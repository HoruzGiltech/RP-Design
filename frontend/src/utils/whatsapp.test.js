import { describe, expect, it } from 'vitest'

import { buildWhatsAppLink } from './whatsapp'

describe('buildWhatsAppLink', () => {
  it('sin mensaje, enlaza solo al número', () => {
    expect(buildWhatsAppLink('584127305964')).toBe('https://wa.me/584127305964')
  })

  it('con mensaje, lo agrega codificado', () => {
    expect(buildWhatsAppLink('584127305964', 'Hola! quiero agendar una reunión')).toBe(
      'https://wa.me/584127305964?text=Hola!%20quiero%20agendar%20una%20reuni%C3%B3n',
    )
  })

  it('codifica los signos que romperían el enlace', () => {
    const link = buildWhatsAppLink('584127305964', '¿Precio & plazo?\nGracias')

    expect(link).toBe(
      'https://wa.me/584127305964?text=%C2%BFPrecio%20%26%20plazo%3F%0AGracias',
    )
  })

  it('limpia el número: solo deja los dígitos', () => {
    expect(buildWhatsAppLink('+58 412-730 5964')).toBe('https://wa.me/584127305964')
  })
})

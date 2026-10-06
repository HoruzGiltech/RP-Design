import { describe, expect, it } from 'vitest'

import { formatUSD } from './currency'

// Los mismos casos que el backend (backend/quotes/tests/test_services.py)
describe('formatUSD', () => {
  it('usa punto para los miles y coma para los decimales', () => {
    expect(formatUSD(1250.5)).toBe('USD 1.250,50')
    expect(formatUSD(1234567.89)).toBe('USD 1.234.567,89')
  })

  it('siempre muestra dos decimales', () => {
    expect(formatUSD(999)).toBe('USD 999,00')
    expect(formatUSD(0.5)).toBe('USD 0,50')
  })

  it('acepta el precio como texto, que es como llega de la API', () => {
    expect(formatUSD('1250.00')).toBe('USD 1.250,00')
  })

  it('muestra "A cotizar" cuando no hay monto', () => {
    expect(formatUSD(null)).toBe('A cotizar')
    expect(formatUSD(undefined)).toBe('A cotizar')
  })
})

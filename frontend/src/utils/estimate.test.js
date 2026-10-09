import { describe, expect, it } from 'vitest'

import { formatUSD } from './currency'
import { calculateEstimate, calculateTotal, parseDecimal } from './estimate'

// Los mismos casos que el backend (backend/quotes/tests/test_services.py)
describe('calculateEstimate', () => {
  it('multiplica los metros cuadrados por el precio del área', () => {
    const estimate = calculateEstimate('100.00', 12.5)

    expect(estimate).toBe(1250)
    expect(formatUSD(estimate)).toBe('USD 1.250,00')
  })

  it('redondea a dos decimales', () => {
    // 33.33 × 3.33 = 110.9889
    expect(calculateEstimate('33.33', 3.33)).toBe(110.99)
  })

  it('redondea la mitad exacta al par, igual que el backend', () => {
    // 0.25 × 0.10 = 0.025 -> 0.02   y   0.35 × 0.10 = 0.035 -> 0.04
    expect(calculateEstimate('0.25', 0.1)).toBe(0.02)
    expect(calculateEstimate('0.35', 0.1)).toBe(0.04)
  })

  it('no sufre los errores de decimales de JavaScript', () => {
    // En JavaScript, 0.1 × 3 da 0.30000000000000004
    expect(calculateEstimate('0.10', 3)).toBe(0.3)
  })

  it('no hay estimado si el área no tiene precio', () => {
    expect(calculateEstimate(null, 20)).toBeNull()
    expect(formatUSD(calculateEstimate(null, 20))).toBe('A cotizar')
  })
})

// specs-003, RF-27: el estimado es la suma de todas las áreas marcadas
describe('calculateTotal', () => {
  it('suma los subtotales de todas las áreas', () => {
    const total = calculateTotal([1000, 400.5])

    expect(total).toBe(1400.5)
    expect(formatUSD(total)).toBe('USD 1.400,50')
  })

  it('no sufre los errores de decimales de JavaScript', () => {
    // En JavaScript, 0.1 + 0.2 da 0.30000000000000004
    expect(calculateTotal([0.1, 0.2])).toBe(0.3)
  })

  it('si un área está "A cotizar", todo el total lo está', () => {
    expect(calculateTotal([1000, null])).toBeNull()
    expect(formatUSD(calculateTotal([1000, null]))).toBe('A cotizar')
  })

  it('sin áreas no hay total', () => {
    expect(calculateTotal([])).toBeNull()
  })
})

describe('parseDecimal', () => {
  it('acepta coma o punto como decimal', () => {
    expect(parseDecimal('12,5')).toBe(12.5)
    expect(parseDecimal('12.5')).toBe(12.5)
    expect(parseDecimal(' 30 ')).toBe(30)
  })

  it('rechaza lo que no es un número', () => {
    expect(parseDecimal('')).toBeNull()
    expect(parseDecimal('doce')).toBeNull()
    expect(parseDecimal('12 m2')).toBeNull()
    expect(parseDecimal('-5')).toBeNull()
  })

  it('rechaza más de dos decimales', () => {
    expect(parseDecimal('12,555')).toBeNull()
  })
})

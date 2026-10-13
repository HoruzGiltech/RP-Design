import { describe, expect, it } from 'vitest'

import { parseDecimal } from './numbers'

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

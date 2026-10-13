import { describe, expect, it } from 'vitest'

import { keepNumberCharacters, parseDecimal } from './numbers'

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

describe('keepNumberCharacters', () => {
  it('conserva las cifras, la coma y el punto', () => {
    expect(keepNumberCharacters('12,5')).toBe('12,5')
    expect(keepNumberCharacters('12.5')).toBe('12.5')
    expect(keepNumberCharacters('120')).toBe('120')
  })

  it('quita las letras, los espacios y los signos', () => {
    expect(keepNumberCharacters('abc')).toBe('')
    expect(keepNumberCharacters('45 metros')).toBe('45')
    expect(keepNumberCharacters('-10')).toBe('10')
    expect(keepNumberCharacters('1e5')).toBe('15')
  })
})

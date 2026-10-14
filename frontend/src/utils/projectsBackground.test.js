import { describe, expect, it } from 'vitest'

import { pickProjectsBackground } from './projectsBackground'

const IMAGE = 'https://api.example.com/media/site/fondo.jpg'
const VIDEO = 'https://api.example.com/media/site/fondo.mp4'

function section(overrides = {}) {
  return {
    show_background: true,
    background_image: IMAGE,
    background_image_alt: 'Obra terminada',
    background_video: VIDEO,
    ...overrides,
  }
}

describe('pickProjectsBackground', () => {
  it('con la casilla desmarcada no hay fondo', () => {
    expect(pickProjectsBackground(section({ show_background: false }), false)).toBeNull()
  })

  it('con la casilla marcada pero sin archivos no hay fondo', () => {
    const empty = section({ background_image: null, background_video: null })

    expect(pickProjectsBackground(empty, false)).toBeNull()
  })

  it('solo con imagen muestra la imagen con su texto alternativo', () => {
    expect(pickProjectsBackground(section({ background_video: null }), false)).toEqual({
      type: 'image',
      src: IMAGE,
      alt: 'Obra terminada',
    })
  })

  it('sin texto alternativo, la imagen queda como decorativa', () => {
    const noAlt = section({ background_video: null, background_image_alt: '' })

    expect(pickProjectsBackground(noAlt, false).alt).toBe('')
  })

  it('con imagen y video muestra el video, con la imagen de vista previa', () => {
    expect(pickProjectsBackground(section(), false)).toEqual({
      type: 'video',
      src: VIDEO,
      poster: IMAGE,
    })
  })

  it('solo con video muestra el video sin vista previa', () => {
    expect(pickProjectsBackground(section({ background_image: null }), false)).toEqual({
      type: 'video',
      src: VIDEO,
      poster: null,
    })
  })

  it('con "reducir movimiento" muestra la imagen en lugar del video', () => {
    expect(pickProjectsBackground(section(), true).type).toBe('image')
  })

  it('con "reducir movimiento" y solo video no hay fondo', () => {
    expect(pickProjectsBackground(section({ background_image: null }), true)).toBeNull()
  })
})

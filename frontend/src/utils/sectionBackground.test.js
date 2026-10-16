import { describe, expect, it } from 'vitest'

import { pickProcessBackground, pickProjectsBackground, shouldShowProcess } from './sectionBackground'

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

const POSTER = 'https://api.example.com/media/site/vista-previa.jpg'

function process(overrides = {}) {
  return { show_video: true, video: VIDEO, video_poster: POSTER, ...overrides }
}

describe('pickProcessBackground', () => {
  it('con la casilla desmarcada no hay fondo', () => {
    expect(pickProcessBackground(process({ show_video: false }), false)).toBeNull()
  })

  it('sin video ni vista previa no hay fondo', () => {
    expect(pickProcessBackground(process({ video: null, video_poster: null }), false)).toBeNull()
  })

  it('con video y vista previa muestra el video, con la vista previa de poster', () => {
    expect(pickProcessBackground(process(), false)).toEqual({
      type: 'video',
      src: VIDEO,
      poster: POSTER,
    })
  })

  it('con "reducir movimiento" muestra la vista previa fija, sin texto alternativo', () => {
    expect(pickProcessBackground(process(), true)).toEqual({ type: 'image', src: POSTER, alt: '' })
  })

  it('con "reducir movimiento" y sin vista previa no hay fondo', () => {
    expect(pickProcessBackground(process({ video_poster: null }), true)).toBeNull()
  })
})

describe('shouldShowProcess', () => {
  const STEP = { id: 1, title: 'Visita técnica', description: 'Medimos el espacio' }
  const VIDEO_BACKGROUND = { type: 'video', src: VIDEO, poster: POSTER }

  it('con pasos se muestra, aunque no haya fondo', () => {
    expect(shouldShowProcess({ is_visible: true, steps: [STEP] }, null)).toBe(true)
  })

  it('sin pasos pero con fondo se muestra (título, introducción y video)', () => {
    expect(shouldShowProcess({ is_visible: true, steps: [] }, VIDEO_BACKGROUND)).toBe(true)
  })

  it('sin pasos ni fondo no se muestra', () => {
    expect(shouldShowProcess({ is_visible: true, steps: [] }, null)).toBe(false)
  })

  it('oculta desde el panel no se muestra, tenga lo que tenga', () => {
    expect(shouldShowProcess({ is_visible: false, steps: [STEP] }, VIDEO_BACKGROUND)).toBe(false)
  })
})

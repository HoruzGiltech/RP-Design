import { describe, expect, it, vi } from 'vitest'

import { preventImageContextMenu, preventImageDrag } from './imageProtection'

function eventFor(tagName) {
  return {
    target: { tagName },
    preventDefault: vi.fn(),
  }
}

describe('preventImageContextMenu', () => {
  it('cancels the context menu for images', () => {
    const event = eventFor('IMG')

    preventImageContextMenu(event)

    expect(event.preventDefault).toHaveBeenCalledOnce()
  })

  it('keeps the context menu for other elements', () => {
    const event = eventFor('P')

    preventImageContextMenu(event)

    expect(event.preventDefault).not.toHaveBeenCalled()
  })

  it('keeps the context menu for videos', () => {
    const event = eventFor('VIDEO')

    preventImageContextMenu(event)

    expect(event.preventDefault).not.toHaveBeenCalled()
  })
})

describe('preventImageDrag', () => {
  it('cancels dragging for images', () => {
    const event = eventFor('IMG')

    preventImageDrag(event)

    expect(event.preventDefault).toHaveBeenCalledOnce()
  })

  it('keeps dragging behavior for other elements', () => {
    const event = eventFor('BUTTON')

    preventImageDrag(event)

    expect(event.preventDefault).not.toHaveBeenCalled()
  })

  it('keeps dragging behavior for videos', () => {
    const event = eventFor('VIDEO')

    preventImageDrag(event)

    expect(event.preventDefault).not.toHaveBeenCalled()
  })
})

export function preventImageContextMenu(event) {
  if (event.target?.tagName === 'IMG') event.preventDefault()
}

export function preventImageDrag(event) {
  if (event.target?.tagName === 'IMG') event.preventDefault()
}

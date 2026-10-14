/**
 * Decide qué fondo lleva la sección Proyectos del inicio (specs-009, RF-65 y RF-66).
 *
 * section:      projects_section de la API. Con la casilla desmarcada, la API
 *               ya manda los archivos en null.
 * reduceMotion: true si el visitante pidió a su sistema menos animaciones
 *
 * Devuelve null (fondo negro de siempre), un video o una imagen.
 */
export function pickProjectsBackground(section, reduceMotion) {
  if (!section.show_background) return null

  const image = section.background_image
  const video = section.background_video

  // Un video que se mueve solo no se muestra a quien pidió menos movimiento:
  // a esa persona le queda la imagen fija
  if (video && !reduceMotion) {
    return { type: 'video', src: video, poster: image || null }
  }

  if (image) {
    return { type: 'image', src: image, alt: section.background_image_alt || '' }
  }

  return null
}

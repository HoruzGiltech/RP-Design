/**
 * Decide qué fondo lleva una sección del inicio: un video, una imagen o nada
 * (specs-009 para Proyectos y specs-011 para Proceso).
 *
 * files:        { video, image, alt }. Con la casilla del panel desmarcada,
 *               la API ya manda los archivos en null.
 * reduceMotion: true si el visitante pidió a su sistema menos animaciones
 *
 * Devuelve null (sin fondo), { type: 'video', src, poster } o { type: 'image', src, alt }.
 */
export function pickSectionBackground({ video, image, alt }, reduceMotion) {
  // Un video que se mueve solo no se muestra a quien pidió menos movimiento:
  // a esa persona le queda la imagen fija
  if (video && !reduceMotion) {
    return { type: 'video', src: video, poster: image || null }
  }

  if (image) {
    return { type: 'image', src: image, alt: alt || '' }
  }

  return null
}

/** Fondo de la sección Proyectos: imagen o video, con su casilla (specs-009). */
export function pickProjectsBackground(section, reduceMotion) {
  if (!section.show_background) return null

  return pickSectionBackground(
    {
      video: section.background_video,
      image: section.background_image,
      alt: section.background_image_alt,
    },
    reduceMotion,
  )
}

/**
 * Fondo de la sección Proceso (specs-011): el video, con su vista previa.
 * La imagen es decoración (el título ya dice de qué trata la sección), por eso
 * va sin texto alternativo.
 */
export function pickProcessBackground(process, reduceMotion) {
  if (!process.show_video) return null

  return pickSectionBackground(
    { video: process.video, image: process.video_poster, alt: '' },
    reduceMotion,
  )
}

/**
 * ¿Se muestra la sección Proceso? (specs-011, RF-70)
 * Con el video de fondo, la sección tiene contenido propio aunque el cliente
 * oculte todos los pasos. Sin pasos ni fondo, quedaría un título suelto.
 */
export function shouldShowProcess(process, background) {
  if (!process.is_visible) return false

  return process.steps.length > 0 || Boolean(background)
}

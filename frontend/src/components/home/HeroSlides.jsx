/**
 * Las portadas del hero, una encima de otra. Solo la activa es visible;
 * el cambio entre ellas es un fundido (ver motion.css).
 *
 * slides:        proyectos del hero (de la API)
 * index:         posición de la portada activa
 * previousIndex: posición de la que se está desvaneciendo
 */
export default function HeroSlides({ slides, index, previousIndex }) {
  const nextIndex = (index + 1) % slides.length

  return slides.map((slide, position) => {
    const isActive = position === index
    // Solo se ponen en la página la portada activa, la que sale y la que viene.
    // Así las demás fotos grandes no se descargan hasta que les toca.
    const isNeeded = isActive || position === previousIndex || position === nextIndex
    if (!isNeeded) return null

    return (
      <img
        key={slide.slug}
        className={isActive ? 'hero__slide is-active' : 'hero__slide'}
        src={slide.cover_image}
        // El texto alternativo solo se anuncia para la portada que se ve
        alt={isActive ? slide.cover_alt : ''}
        aria-hidden={isActive ? undefined : 'true'}
        // La primera es lo más importante de la página: se carga con prioridad
        fetchPriority={position === 0 ? 'high' : 'low'}
      />
    )
  })
}

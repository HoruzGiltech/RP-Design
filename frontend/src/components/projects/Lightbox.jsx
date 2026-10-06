import { useEffect, useRef } from 'react'

import './Lightbox.css'

/**
 * Visor de imágenes en grande.
 *
 * Usa la etiqueta <dialog> del navegador, que ya trae lo difícil resuelto:
 * se cierra con Esc, mantiene el foco del teclado dentro del visor y, al
 * cerrarse, devuelve el foco a la miniatura que lo abrió.
 *
 * images:     lista de { id, file, alt_text }
 * index:      posición de la imagen que se está viendo
 * onNavigate: recibe la nueva posición al pasar de imagen
 * onClose:    se llama cuando el visor se cierra
 */
export default function Lightbox({ images, index, onNavigate, onClose }) {
  const dialogRef = useRef(null)
  const image = images[index]
  const hasSeveral = images.length > 1

  // Al aparecer el componente, se abre el diálogo en modo "modal".
  // No hace falta cerrarlo al desaparecer: React quita el <dialog> de la página.
  // (Cerrarlo aquí dispararía el evento "close" y, con él, onClose por error.)
  useEffect(() => {
    const dialog = dialogRef.current
    if (!dialog.open) dialog.showModal()
  }, [])

  // Al llegar al final se vuelve a la primera, y al revés
  function showPrevious() {
    onNavigate((index - 1 + images.length) % images.length)
  }

  function showNext() {
    onNavigate((index + 1) % images.length)
  }

  function handleKeyDown(event) {
    if (!hasSeveral) return
    if (event.key === 'ArrowLeft') showPrevious()
    if (event.key === 'ArrowRight') showNext()
  }

  // Un clic en el fondo oscuro (fuera de la imagen y los botones) cierra el visor
  function handleClick(event) {
    if (event.target === dialogRef.current) onClose()
  }

  return (
    <dialog
      ref={dialogRef}
      className="lightbox"
      aria-label="Visor de imágenes"
      // "close" se dispara al cerrar con Esc
      onClose={onClose}
      onKeyDown={handleKeyDown}
      onClick={handleClick}
    >
      <button type="button" className="lightbox__button lightbox__close" onClick={onClose}>
        Cerrar
      </button>

      {/* key: al cambiar de imagen se repite la animación de entrada */}
      <img key={image.id} className="lightbox__image" src={image.file} alt={image.alt_text} />

      {hasSeveral && (
        <div className="lightbox__nav">
          <button type="button" className="lightbox__button" onClick={showPrevious}>
            <span aria-hidden="true">←</span> Anterior
          </button>
          <span className="lightbox__counter">
            {index + 1} / {images.length}
          </span>
          <button type="button" className="lightbox__button" onClick={showNext}>
            Siguiente <span aria-hidden="true">→</span>
          </button>
        </div>
      )}
    </dialog>
  )
}

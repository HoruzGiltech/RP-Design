/**
 * Dibuja el fondo que eligió pickSectionBackground (utils/sectionBackground.js):
 * un video o una imagen que cubre toda la sección. Lo usan Proyectos
 * (specs-009) y Proceso (specs-011), a través de la propiedad background de Section.
 */
export default function SectionBackground({ background }) {
  if (background.type === 'video') {
    return (
      <video
        className="section__background"
        src={background.src}
        poster={background.poster || undefined}
        // Sin sonido: es la condición de los navegadores para reproducir un video solo
        muted
        autoPlay
        loop
        playsInline
        // Sin "controls" no se dibuja ningún botón. Estas dos quitan los botones
        // flotantes que algunos navegadores agregan por su cuenta
        disablePictureInPicture
        disableRemotePlayback
        // Solo pide los datos básicos hasta que empieza a reproducirse
        preload="metadata"
        // Es decoración: el título ya dice de qué trata la sección
        aria-hidden="true"
      />
    )
  }

  return <img className="section__background" src={background.src} alt={background.alt} decoding="async" />
}

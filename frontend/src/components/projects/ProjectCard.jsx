import { Link } from 'react-router-dom'

import { useInCenter } from '../../hooks/useInCenter'
import MediaPlaceholder from '../media/MediaPlaceholder'
import Reveal from '../ui/Reveal'
import '../../styles/overlay.css'
import './ProjectCard.css'

/**
 * Tarjeta de un proyecto: foto, categoría, título y resumen.
 * Toda la tarjeta es un enlace a la página del proyecto.
 * Está pensada para ir sobre fondo oscuro (inicio y /proyectos).
 *
 * index:   posición en la cuadrícula, para que las tarjetas entren una tras otra.
 * titleAs: nivel del título ("h2" o "h3"). Depende de la página: los títulos deben
 *          bajar de nivel en orden (h1, h2, h3), sin saltarse ninguno.
 */
export default function ProjectCard({ project, index = 0, titleAs: Title = 'h3' }) {
  // En un celular, la capa aparece cuando la tarjeta cruza el centro de la pantalla
  const { ref, isInCenter } = useInCenter()
  const mediaClasses = ['project-card__media', 'has-cover-overlay', isInCenter ? 'is-centered' : '']
    .filter(Boolean)
    .join(' ')

  return (
    <Reveal as="article" index={index} className="project-card">
      <Link to={`/proyectos/${project.slug}`} className="project-card__link">
        <div ref={ref} className={mediaClasses}>
          {project.cover_thumbnail ? (
            <img
              className="project-card__image"
              src={project.cover_thumbnail}
              alt={project.cover_alt}
              // Las tarjetas que están más abajo no se descargan hasta que hacen falta
              loading="lazy"
            />
          ) : (
            <MediaPlaceholder variant="dark" />
          )}
          {/*
            Capa con la descripción completa del proyecto (specs-003, RF-22;
            estilos en styles/overlay.css). Aparece al pasar el cursor o, en un
            celular, al cruzar la tarjeta el centro de la pantalla. Va oculta
            para lectores de pantalla: el enlace ya tiene su texto y la
            descripción se lee en la página del proyecto.
          */}
          {project.description && (
            <span className="cover-overlay" aria-hidden="true">
              <span className="cover-overlay__content">
                <span className="cover-overlay__text">{project.description}</span>
              </span>
            </span>
          )}
        </div>

        <div className="project-card__text">
          {project.category && (
            <p className="project-card__category">{project.category.name}</p>
          )}
          <Title className="project-card__title">{project.title}</Title>
          <p className="project-card__summary">{project.summary}</p>
        </div>
      </Link>
    </Reveal>
  )
}

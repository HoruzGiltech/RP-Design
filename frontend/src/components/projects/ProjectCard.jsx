import { Link } from 'react-router-dom'

import MediaPlaceholder from '../media/MediaPlaceholder'
import Reveal from '../ui/Reveal'
import './ProjectCard.css'

/**
 * Tarjeta de un proyecto: foto, categoría, título y resumen.
 * Toda la tarjeta es un enlace a la página del proyecto.
 * Está pensada para ir sobre fondo oscuro (inicio y /proyectos).
 *
 * index: posición en la cuadrícula, para que las tarjetas entren una tras otra.
 */
export default function ProjectCard({ project, index = 0 }) {
  return (
    <Reveal as="article" index={index} className="project-card">
      <Link to={`/proyectos/${project.slug}`} className="project-card__link">
        <div className="project-card__media">
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
          {/* Capa que aparece al pasar el cursor; es un adorno, el enlace ya tiene su texto */}
          <span className="project-card__overlay" aria-hidden="true">
            Ver proyecto
          </span>
        </div>

        {project.category && <p className="project-card__category">{project.category}</p>}
        <h3 className="project-card__title">{project.title}</h3>
        <p className="project-card__summary">{project.summary}</p>
      </Link>
    </Reveal>
  )
}

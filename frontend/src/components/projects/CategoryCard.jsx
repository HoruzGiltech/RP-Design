import { Link } from 'react-router-dom'

import MediaPlaceholder from '../media/MediaPlaceholder'
import Reveal from '../ui/Reveal'
// Usa los mismos estilos que la tarjeta de proyecto: se ven iguales a propósito
import './ProjectCard.css'

/** "1 proyecto", "4 proyectos" */
function formatProjectCount(count) {
  return count === 1 ? '1 proyecto' : `${count} proyectos`
}

/**
 * Tarjeta de una categoría en el inicio. Lleva a /proyectos mostrando solo
 * los proyectos de esa categoría.
 *
 * category: { name, slug, project_count, cover_thumbnail, cover_alt } (de la API)
 * index:    posición en la cuadrícula, para que las tarjetas entren una tras otra
 */
export default function CategoryCard({ category, index = 0 }) {
  return (
    <Reveal as="article" index={index} className="project-card">
      <Link to={`/proyectos?categoria=${category.slug}`} className="project-card__link">
        <div className="project-card__media">
          {category.cover_thumbnail ? (
            <img
              className="project-card__image"
              src={category.cover_thumbnail}
              alt={category.cover_alt}
              loading="lazy"
            />
          ) : (
            <MediaPlaceholder variant="dark" />
          )}
          <span className="project-card__overlay" aria-hidden="true">
            Ver proyectos
          </span>
        </div>

        <h3 className="project-card__title">{category.name}</h3>
        <p className="project-card__summary">{formatProjectCount(category.project_count)}</p>
      </Link>
    </Reveal>
  )
}

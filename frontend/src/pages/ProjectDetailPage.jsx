import { Link, useParams } from 'react-router-dom'

import { getProject } from '../api/endpoints'
import MediaGallery from '../components/projects/MediaGallery'
import ErrorMessage from '../components/ui/ErrorMessage'
import Reveal from '../components/ui/Reveal'
import Section from '../components/ui/Section'
import Spinner from '../components/ui/Spinner'
import { useDocumentTitle } from '../hooks/useDocumentTitle'
import { useFetch } from '../hooks/useFetch'
import NotFoundPage from './NotFoundPage'
import './ProjectDetailPage.css'

const NOT_FOUND = 404

/** /proyectos/<slug>: la página propia de cada proyecto. */
export default function ProjectDetailPage() {
  const { slug } = useParams()
  // [slug]: si se pasa de un proyecto a otro, se piden los datos del nuevo
  const { data: project, loading, error, reload } = useFetch(() => getProject(slug), [slug])

  if (loading) return <Spinner label="Cargando proyecto…" />

  // Un proyecto que no existe o que es borrador: el backend responde 404
  if (error?.status === NOT_FOUND) {
    return (
      <NotFoundPage
        title="Proyecto no encontrado"
        message="Este proyecto no existe o ya no está publicado."
      />
    )
  }
  if (error) return <ErrorMessage message={error.message} onRetry={reload} />

  return <ProjectDetail project={project} />
}

function ProjectDetail({ project }) {
  useDocumentTitle(project.title, project.summary)

  // Ubicación y año en una sola línea, solo con los datos que existan
  const details = [project.location, project.year].filter(Boolean).join(' · ')

  return (
    <Section variant="dark" className="project-detail">
      <header className="project-detail__header">
        <Link to="/proyectos" className="project-detail__back">
          <span aria-hidden="true">←</span> Todos los proyectos
        </Link>
        {project.category && (
          <Reveal as="p" className="project-detail__category">
            {project.category.name}
          </Reveal>
        )}
        <Reveal as="h1" index={1} className="project-detail__title">
          {project.title}
        </Reveal>
        {details && (
          <Reveal as="p" index={2} className="project-detail__details">
            {details}
          </Reveal>
        )}
      </header>

      <div className="project-detail__cover">
        <img
          className="project-detail__cover-image zoom-on-scroll"
          src={project.cover_image}
          alt={project.cover_alt}
          fetchPriority="high"
        />
      </div>

      <Reveal as="p" className="project-detail__description">
        {project.description}
      </Reveal>

      <MediaGallery media={project.media} />
    </Section>
  )
}

import { getFeaturedProjects } from '../../api/endpoints'
import { useSite } from '../../context/SiteContext'
import { useFetch } from '../../hooks/useFetch'
import ProjectGrid from '../projects/ProjectGrid'
import Button from '../ui/Button'
import ErrorMessage from '../ui/ErrorMessage'
import Reveal from '../ui/Reveal'
import Section from '../ui/Section'
import './FeaturedProjects.css'

/** Sección "Proyectos" del inicio: los destacados que eligió el cliente (máximo 3). */
export default function FeaturedProjects() {
  const { data: site } = useSite()
  const { data: projects, loading, error, reload } = useFetch(getFeaturedProjects)

  const { projects_section: section, settings } = site

  if (!section.is_visible) return null
  // Mientras carga no se dibuja nada, para no mostrar un título sin tarjetas
  if (loading) return null
  // Sin destacados, la sección completa se oculta (no queda un bloque vacío)
  if (!error && projects.length === 0) return null

  return (
    <Section id="proyectos" variant="dark" className="featured-projects">
      <div className="featured-projects__header">
        <Reveal as="h2">{section.title}</Reveal>
        {settings.instagram_url && (
          <Reveal
            as="a"
            index={1}
            className="featured-projects__instagram"
            href={settings.instagram_url}
            target="_blank"
            rel="noopener noreferrer"
          >
            {section.instagram_link_text} @{settings.instagram_handle}
          </Reveal>
        )}
      </div>

      {error ? (
        <ErrorMessage message={error.message} onRetry={reload} />
      ) : (
        <ProjectGrid projects={projects} />
      )}

      <div>
        <Button to="/proyectos" variant="secondary" onDark>
          {section.view_all_text}
        </Button>
      </div>
    </Section>
  )
}

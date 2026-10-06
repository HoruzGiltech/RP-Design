import { getProjects } from '../api/endpoints'
import ProjectGrid from '../components/projects/ProjectGrid'
import ErrorMessage from '../components/ui/ErrorMessage'
import Reveal from '../components/ui/Reveal'
import Section from '../components/ui/Section'
import Spinner from '../components/ui/Spinner'
import { useDocumentTitle } from '../hooks/useDocumentTitle'
import { useFetch } from '../hooks/useFetch'
import './ProjectsPage.css'

const PAGE_TITLE = 'Proyectos'

/** /proyectos: todos los proyectos publicados, en el orden del panel. */
export default function ProjectsPage() {
  const { data: projects, loading, error, reload } = useFetch(getProjects)

  useDocumentTitle(PAGE_TITLE)

  return (
    <Section variant="dark" className="projects-page">
      <Reveal as="h1" className="projects-page__title">
        {PAGE_TITLE}
      </Reveal>
      <ProjectsContent projects={projects} loading={loading} error={error} onRetry={reload} />
    </Section>
  )
}

/** Los tres estados de la página: cargando, error y lista (que puede estar vacía). */
function ProjectsContent({ projects, loading, error, onRetry }) {
  if (loading) return <Spinner label="Cargando proyectos…" />
  if (error) return <ErrorMessage message={error.message} onRetry={onRetry} />
  if (projects.length === 0) {
    return <p className="projects-page__empty">Todavía no hay proyectos publicados.</p>
  }
  // En esta página las tarjetas van justo debajo del h1, así que sus títulos son h2
  return <ProjectGrid projects={projects} titleAs="h2" />
}

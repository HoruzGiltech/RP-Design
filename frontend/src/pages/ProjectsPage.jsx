import { useSearchParams } from 'react-router-dom'

import { getProjectCategories, getProjects } from '../api/endpoints'
import CategoryFilter from '../components/projects/CategoryFilter'
import ProjectGrid from '../components/projects/ProjectGrid'
import ErrorMessage from '../components/ui/ErrorMessage'
import Reveal from '../components/ui/Reveal'
import Section from '../components/ui/Section'
import Spinner from '../components/ui/Spinner'
import { useSite } from '../context/SiteContext'
import { useDocumentTitle } from '../hooks/useDocumentTitle'
import { useFetch } from '../hooks/useFetch'
import './ProjectsPage.css'

// Título de respaldo, por si el cliente deja vacío el de la sección
const DEFAULT_TITLE = 'Proyectos'
// Nombre del parámetro en la dirección: /proyectos?categoria=residencial
const CATEGORY_PARAM = 'categoria'

/**
 * /proyectos: todos los proyectos publicados, o solo los de una categoría
 * si la dirección trae ?categoria=<slug> (specs-001, RF-09).
 */
export default function ProjectsPage() {
  const { data: site } = useSite()
  const [searchParams] = useSearchParams()
  const requestedSlug = searchParams.get(CATEGORY_PARAM)

  const { data: categories } = useFetch(getProjectCategories)
  // [requestedSlug]: al cambiar de categoría se piden los proyectos de la nueva
  const {
    data: projects,
    loading,
    error,
    reload,
  } = useFetch(() => getProjects(requestedSlug), [requestedSlug])

  // Si la categoría de la dirección no existe, la página se comporta como "Todos"
  const activeCategory = (categories ?? []).find((category) => category.slug === requestedSlug)
  // La página se llama igual que la sección Proyectos del inicio (specs-003, RF-21)
  const pageTitle = site.projects_section.title || DEFAULT_TITLE
  const title = activeCategory ? activeCategory.name : pageTitle

  useDocumentTitle(activeCategory ? `${activeCategory.name} | ${pageTitle}` : pageTitle)

  return (
    <Section variant="dark" className="projects-page">
      {/* key: al cambiar de categoría, el título vuelve a entrar con su animación */}
      <Reveal as="h1" key={title} className="projects-page__title">
        {title}
      </Reveal>
      {categories && categories.length > 0 && (
        <CategoryFilter categories={categories} activeSlug={activeCategory?.slug ?? null} />
      )}
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

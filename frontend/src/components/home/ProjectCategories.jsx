import { getProjectCategories } from '../../api/endpoints'
import { useSite } from '../../context/SiteContext'
import { useFetch } from '../../hooks/useFetch'
import CategoryCard from '../projects/CategoryCard'
import Button from '../ui/Button'
import ErrorMessage from '../ui/ErrorMessage'
import Reveal from '../ui/Reveal'
import Section from '../ui/Section'
import './ProjectCategories.css'

/**
 * Sección "Proyectos" del inicio: una tarjeta por categoría (specs-001, RF-09).
 * Solo llegan de la API las categorías que tienen proyectos publicados.
 */
export default function ProjectCategories() {
  const { data: site } = useSite()
  const { data: categories, loading, error, reload } = useFetch(getProjectCategories)

  const { projects_section: section, settings } = site

  if (!section.is_visible) return null
  // Mientras carga no se dibuja nada, para no mostrar un título sin tarjetas
  if (loading) return null
  // Sin categorías con proyectos, la sección completa se oculta
  if (!error && categories.length === 0) return null

  return (
    <Section id="proyectos" variant="dark" className="project-categories">
      <div className="project-categories__header">
        <Reveal as="h2">{section.title}</Reveal>
        {settings.instagram_url && (
          <Reveal
            as="a"
            index={1}
            className="project-categories__instagram"
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
        <div className="project-grid">
          {categories.map((category, position) => (
            <CategoryCard key={category.slug} category={category} index={position} />
          ))}
        </div>
      )}

      <div>
        <Button to="/proyectos" variant="secondary" onDark>
          {section.view_all_text}
        </Button>
      </div>
    </Section>
  )
}

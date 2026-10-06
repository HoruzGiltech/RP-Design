import { getLegalPage } from '../api/endpoints'
import ErrorMessage from '../components/ui/ErrorMessage'
import Section from '../components/ui/Section'
import Spinner from '../components/ui/Spinner'
import { useDocumentTitle } from '../hooks/useDocumentTitle'
import { useFetch } from '../hooks/useFetch'
import NotFoundPage from './NotFoundPage'
import './LegalPage.css'

const NOT_FOUND = 404

/** "2026-10-06T14:00:00Z" -> "6 de octubre de 2026" */
function formatDate(isoDate) {
  return new Date(isoDate).toLocaleDateString('es', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })
}

/**
 * Página legal: /terminos o /privacidad.
 * `slug` indica cuál; lo pone cada ruta en App.jsx.
 * El contenido se edita en el panel, en "Páginas legales".
 */
export default function LegalPage({ slug }) {
  const { data: page, loading, error, reload } = useFetch(() => getLegalPage(slug), [slug])

  if (loading) return <Spinner />
  if (error?.status === NOT_FOUND) return <NotFoundPage />
  if (error) return <ErrorMessage message={error.message} onRetry={reload} />

  return <LegalContent page={page} />
}

function LegalContent({ page }) {
  useDocumentTitle(page.title)

  return (
    <Section className="legal-page">
      <header className="legal-page__header">
        <h1 className="legal-page__title">{page.title}</h1>
        <p className="legal-page__date">Última actualización: {formatDate(page.updated_at)}</p>
      </header>

      {page.intro && <p className="legal-page__intro">{page.intro}</p>}

      {page.sections.map((section) => (
        <section key={section.id} className="legal-page__section">
          <h2 className="legal-page__subtitle">{section.title}</h2>
          <p className="legal-page__text">{section.body}</p>
        </section>
      ))}
    </Section>
  )
}

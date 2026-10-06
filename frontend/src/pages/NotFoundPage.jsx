import Button from '../components/ui/Button'
import Section from '../components/ui/Section'
import { useDocumentTitle } from '../hooks/useDocumentTitle'
import './NotFoundPage.css'

/**
 * Página para una dirección que no existe. También la usa el detalle de
 * proyecto cuando el proyecto no existe o es un borrador.
 */
export default function NotFoundPage({
  title = 'Página no encontrada',
  message = 'La dirección que abriste no existe o cambió de lugar.',
}) {
  useDocumentTitle(title)

  return (
    <Section className="not-found">
      <h1 className="not-found__title">{title}</h1>
      <p className="not-found__message">{message}</p>
      <div className="not-found__actions">
        <Button to="/">Volver al inicio</Button>
        <Button to="/proyectos" variant="secondary">
          Ver proyectos
        </Button>
      </div>
    </Section>
  )
}

import Contact from '../components/home/Contact'
import Hero from '../components/home/Hero'
import Process from '../components/home/Process'
import ProjectsTeaser from '../components/home/ProjectsTeaser'
import Services from '../components/home/Services'
import QuoteCalculator from '../components/quote/QuoteCalculator'
import { useDocumentTitle } from '../hooks/useDocumentTitle'

/**
 * Página de inicio, en el orden que pidió el cliente (specs-008): Servicios
 * con portadas (negro), Proyectos (negro), Proceso en tarjetas numeradas
 * (claro) y Contacto. El menú del encabezado conserva su propio orden.
 * Cada sección decide por sí misma si se muestra (según el panel).
 */
export default function HomePage() {
  // Sin argumentos: el título es el nombre del sitio
  useDocumentTitle()

  return (
    <>
      <Hero />
      <Services />
      <ProjectsTeaser />
      <Process />
      <Contact>
        <QuoteCalculator />
      </Contact>
    </>
  )
}

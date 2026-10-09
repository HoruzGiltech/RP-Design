import Contact from '../components/home/Contact'
import Hero from '../components/home/Hero'
import Process from '../components/home/Process'
import ProjectCategories from '../components/home/ProjectCategories'
import Services from '../components/home/Services'
import QuoteCalculator from '../components/quote/QuoteCalculator'
import { useDocumentTitle } from '../hooks/useDocumentTitle'

/**
 * Página de inicio: las secciones de la maqueta, en el orden que pidió el
 * cliente: Proyectos primero (specs-001, P-8) y Proceso antes que Servicios
 * (specs-003, RF-23). El menú del encabezado conserva su propio orden.
 * Cada sección decide por sí misma si se muestra (según el panel).
 */
export default function HomePage() {
  // Sin argumentos: el título es el nombre del sitio
  useDocumentTitle()

  return (
    <>
      <Hero />
      <ProjectCategories />
      <Process />
      <Services />
      <Contact>
        <QuoteCalculator />
      </Contact>
    </>
  )
}

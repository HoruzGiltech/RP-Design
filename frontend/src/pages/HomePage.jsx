import Contact from '../components/home/Contact'
import Hero from '../components/home/Hero'
import Process from '../components/home/Process'
import ProjectCategories from '../components/home/ProjectCategories'
import Services from '../components/home/Services'
import SpecialtiesStrip from '../components/home/SpecialtiesStrip'
import QuoteCalculator from '../components/quote/QuoteCalculator'
import { useDocumentTitle } from '../hooks/useDocumentTitle'

/**
 * Página de inicio: las secciones de la maqueta. Proyectos va antes de
 * Servicios porque así lo pidió el cliente (specs-001, P-8).
 * Cada sección decide por sí misma si se muestra (según el panel).
 */
export default function HomePage() {
  // Sin argumentos: el título es el nombre del sitio
  useDocumentTitle()

  return (
    <>
      <Hero />
      <SpecialtiesStrip />
      <ProjectCategories />
      <Services />
      <Process />
      <Contact>
        <QuoteCalculator />
      </Contact>
    </>
  )
}

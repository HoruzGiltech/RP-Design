import Contact from '../components/home/Contact'
import FeaturedProjects from '../components/home/FeaturedProjects'
import Hero from '../components/home/Hero'
import Process from '../components/home/Process'
import Services from '../components/home/Services'
import SpecialtiesStrip from '../components/home/SpecialtiesStrip'
import { useDocumentTitle } from '../hooks/useDocumentTitle'

/**
 * Página de inicio: las secciones de la maqueta, en su mismo orden.
 * Cada sección decide por sí misma si se muestra (según el panel).
 */
export default function HomePage() {
  // Sin argumentos: el título es el nombre del sitio
  useDocumentTitle()

  return (
    <>
      <Hero />
      <SpecialtiesStrip />
      <Services />
      <FeaturedProjects />
      <Process />
      <Contact />
    </>
  )
}

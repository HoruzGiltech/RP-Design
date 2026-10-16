import { useSite } from '../../context/SiteContext'
import { prefersReducedMotion } from '../../hooks/useReveal'
import { pickProjectsBackground } from '../../utils/sectionBackground'
import Button from '../ui/Button'
import Reveal from '../ui/Reveal'
import Section from '../ui/Section'
import SectionBackground from '../ui/SectionBackground'
import './ProjectsTeaser.css'

/**
 * Sección "Proyectos" del inicio: el título, el enlace a Instagram y un botón
 * grande que lleva a /proyectos (specs-004, RF-34). Los proyectos y sus
 * categorías se ven en esa página. Puede llevar una imagen o un video de
 * fondo, que se elige en el panel (specs-009).
 */
export default function ProjectsTeaser() {
  const { data: site } = useSite()
  const { projects_section: section, settings } = site

  if (!section.is_visible) return null

  const background = pickProjectsBackground(section, prefersReducedMotion())

  return (
    <Section
      id="proyectos"
      variant="dark"
      className={background ? 'projects-teaser projects-teaser--with-background' : 'projects-teaser'}
      background={background && <SectionBackground background={background} />}
    >
      <div className="projects-teaser__header">
        <Reveal as="h2">{section.title}</Reveal>
        {settings.instagram_url && (
          <Reveal
            as="a"
            index={1}
            className="projects-teaser__instagram"
            href={settings.instagram_url}
            target="_blank"
            rel="noopener noreferrer"
          >
            {section.instagram_link_text} @{settings.instagram_handle}
          </Reveal>
        )}
      </div>

      {section.view_all_text && (
        <Reveal index={2}>
          <Button to="/proyectos" size="large" onDark>
            {section.view_all_text}
            {/* Adorno: la flecha se desplaza al pasar el cursor (ver Button.css) */}
            <span className="button__arrow" aria-hidden="true">
              →
            </span>
          </Button>
        </Reveal>
      )}
    </Section>
  )
}

import { useSite } from '../../context/SiteContext'
import { prefersReducedMotion } from '../../hooks/useReveal'
import { pickProcessBackground } from '../../utils/sectionBackground'
import Reveal from '../ui/Reveal'
import Section from '../ui/Section'
import SectionBackground from '../ui/SectionBackground'
import './Process.css'

/** 0 -> "01", 1 -> "02"... El número sale de la posición, no se guarda en el panel. */
function formatNumber(position) {
  return String(position + 1).padStart(2, '0')
}

/**
 * Sección Proceso: el título, la introducción y los pasos como tarjetas
 * numeradas (specs-008, RF-58). Si el cliente dejó marcada la casilla del
 * panel y cargó un video, ese video es el fondo de toda la sección: se
 * reproduce solo, sin sonido y sin botones (specs-011, RF-68 y RF-69).
 */
export default function Process() {
  const { data: site } = useSite()
  const { process } = site

  // Oculta desde el panel, o sin pasos que mostrar: no se deja un título suelto
  if (!process.is_visible || process.steps.length === 0) return null

  const background = pickProcessBackground(process, prefersReducedMotion())

  return (
    <Section
      id="proceso"
      className={background ? 'process process--with-background' : 'process'}
      background={background && <SectionBackground background={background} />}
    >
      <div className="process__header">
        <Reveal as="h2">{process.title}</Reveal>
        {process.intro && (
          <Reveal as="p" index={1} className="process__intro">
            {process.intro}
          </Reveal>
        )}
      </div>

      {/* <ol>: los pasos tienen un orden, y un lector de pantalla lo anuncia */}
      <ol className="process__grid">
        {process.steps.map((step, position) => (
          <Reveal as="li" key={step.id} index={position} className="process__card">
            <span className="process__number" aria-hidden="true">
              {formatNumber(position)}
            </span>
            <h3 className="process__title">{step.title}</h3>
            <p className="process__description">{step.description}</p>
          </Reveal>
        ))}
      </ol>
    </Section>
  )
}

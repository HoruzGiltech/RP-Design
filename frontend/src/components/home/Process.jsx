import { useSite } from '../../context/SiteContext'
import MediaPlaceholder from '../media/MediaPlaceholder'
import Reveal from '../ui/Reveal'
import Section from '../ui/Section'
import './Process.css'

const LETTER_A_CODE = 65

/** 0 -> "A", 1 -> "B"... La letra sale de la posición, no se guarda en el panel. */
function formatLetter(position) {
  return String.fromCharCode(LETTER_A_CODE + position)
}

/** Video recorrido, su imagen de vista previa o un recuadro liso. */
function ProcessMedia({ process }) {
  if (process.video) {
    return (
      // Con controles y sin reproducción automática: lo inicia el visitante
      <video
        className="process__media-item"
        src={process.video}
        poster={process.video_poster || undefined}
        controls
        preload="metadata"
        playsInline
      />
    )
  }
  if (process.video_poster) {
    // Solo hay imagen de vista previa: se muestra como adorno
    return <img className="process__media-item" src={process.video_poster} alt="" loading="lazy" />
  }
  return <MediaPlaceholder variant="light" />
}

export default function Process() {
  const { data: site } = useSite()
  const { process } = site

  if (!process.is_visible || process.steps.length === 0) return null

  return (
    <Section id="proceso" className="process">
      <div className="process__intro-column">
        <Reveal as="h2">{process.title}</Reveal>
        {process.intro && (
          <Reveal as="p" index={1} className="process__intro">
            {process.intro}
          </Reveal>
        )}
        <Reveal index={2} className="process__media">
          <ProcessMedia process={process} />
        </Reveal>
      </div>

      <ol className="process__steps">
        {process.steps.map((step, position) => (
          <Reveal as="li" key={step.id} index={position} className="process__step">
            <span className="process__letter" aria-hidden="true">
              {formatLetter(position)}
            </span>
            <div className="process__step-text">
              <h3>{step.title}</h3>
              <p className="process__step-description">{step.description}</p>
            </div>
          </Reveal>
        ))}
      </ol>
    </Section>
  )
}

import { useSite } from '../context/SiteContext'
import Button from '../components/ui/Button'
import Reveal from '../components/ui/Reveal'
import Section from '../components/ui/Section'

/*
  Página de inicio. Por ahora es provisional: muestra los componentes base
  con los textos de la API. Las secciones reales llegan en T-3.6 a T-3.8.
*/
export default function HomePage() {
  const { data: site } = useSite()

  return (
    <>
      <Section id="inicio">
        <Reveal as="h1">{site.hero.title}</Reveal>
        <Reveal as="p" index={1}>
          {site.hero.body}
        </Reveal>
        <Reveal from="right" index={2}>
          <Button to="/#contacto">{site.hero.primary_cta_text}</Button>{' '}
          <Button to="/#proyectos" variant="secondary">
            {site.hero.secondary_cta_text}
          </Button>
        </Reveal>
      </Section>
      <Section id="servicios">
        <Reveal as="h2">{site.services.title}</Reveal>
      </Section>
      <Section id="proyectos" variant="dark">
        <Reveal as="h2">{site.projects_section.title}</Reveal>
        <Button to="/proyectos" variant="secondary" onDark>
          {site.projects_section.view_all_text}
        </Button>
      </Section>
      <Section id="proceso">
        <Reveal as="h2">{site.process.title}</Reveal>
      </Section>
      <Section id="contacto" variant="alt">
        <Reveal as="h2">{site.contact.title}</Reveal>
      </Section>
    </>
  )
}

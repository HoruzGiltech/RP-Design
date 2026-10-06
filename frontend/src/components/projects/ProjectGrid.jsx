import ProjectCard from './ProjectCard'
import './ProjectGrid.css'

/**
 * Cuadrícula de tarjetas de proyecto. La usan el inicio y la página /proyectos.
 * titleAs: nivel del título de cada tarjeta (ver ProjectCard).
 */
export default function ProjectGrid({ projects, titleAs }) {
  return (
    <div className="project-grid">
      {projects.map((project, position) => (
        <ProjectCard key={project.slug} project={project} index={position} titleAs={titleAs} />
      ))}
    </div>
  )
}

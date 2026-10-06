import ProjectCard from './ProjectCard'
import './ProjectGrid.css'

/** Cuadrícula de tarjetas de proyecto. La usan el inicio y la página /proyectos. */
export default function ProjectGrid({ projects }) {
  return (
    <div className="project-grid">
      {projects.map((project, position) => (
        <ProjectCard key={project.slug} project={project} index={position} />
      ))}
    </div>
  )
}

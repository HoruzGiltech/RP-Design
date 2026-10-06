import { Link } from 'react-router-dom'

import './CategoryFilter.css'

/**
 * Filtro de la página /proyectos: "Todos" y cada categoría.
 *
 * Son enlaces y no botones: así cada filtro tiene su propia dirección, se
 * puede compartir y funciona el botón "atrás" del navegador.
 *
 * categories: categorías con proyectos publicados (de la API)
 * activeSlug: dirección de la categoría elegida, o null para "Todos"
 */
export default function CategoryFilter({ categories, activeSlug }) {
  const options = [
    { label: 'Todos', slug: null, to: '/proyectos' },
    ...categories.map((category) => ({
      label: category.name,
      slug: category.slug,
      to: `/proyectos?categoria=${category.slug}`,
    })),
  ]

  return (
    <nav aria-label="Categorías de proyectos" className="category-filter">
      {options.map((option) => (
        <Link
          key={option.to}
          to={option.to}
          className="category-filter__link"
          // aria-current marca cuál está elegido, para la vista y para lectores de pantalla
          aria-current={option.slug === activeSlug ? 'page' : undefined}
        >
          {option.label}
        </Link>
      ))}
    </nav>
  )
}

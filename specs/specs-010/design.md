# Diseño — specs-010

> **Cómo** se construyen los requisitos de `specs/specs-010/requirements.md`.

**Estado:** Implementado y cerrado (2026-10-14)

---

## 1. Qué se toca

Solo el frontend: `pages/ProjectsPage.jsx` y `pages/ProjectsPage.css`. Sin backend, sin migraciones y sin dependencias nuevas.

## 2. Componente

En `ProjectsPage`, antes del título:

```jsx
<Link to="/#proyectos" className="projects-page__back">
  <span className="projects-page__back-arrow" aria-hidden="true">←</span> Volver
</Link>
```

- `Link` de React Router, como el enlace del detalle del proyecto.
- La flecha lleva `aria-hidden`: un lector de pantalla solo lee "Volver".
- El inicio ya sabe bajar a una sección cuando la dirección trae `#…` (lo usa el menú con `/#proyectos`). Se comprueba en el navegador.
- Va fuera de `Reveal`: está siempre visible, sin animación de entrada, para que se vea de inmediato.

## 3. CSS

- `.projects-page__back`: `display: inline-flex`, `align-items: center`, `gap: 8px`, `min-height: 44px`, `align-self: flex-start`, color `var(--color-on-dark)` (blanco), `font-size: var(--text-nav)`, sin subrayado.
- Como la página es una columna con `gap` de 48 px, el enlace queda pegado al título con un margen negativo abajo (`margin-bottom: calc(var(--space-16) - var(--space-48))`), para que se lea como parte del encabezado y no como un bloque suelto.
- `@media (hover: hover)`: al pasar el cursor, `.projects-page__back-arrow` se mueve `translateX(-4px)` con `var(--motion-hover)`.
- `@media (prefers-reduced-motion: reduce)`: sin desplazamiento.
- Foco: el contorno global del sitio (`:focus-visible`).

## 4. Pruebas

No hay lógica que probar con Vitest (es un enlace fijo). Se comprueba en el navegador con Playwright, en escritorio y en celular: que se ve en blanco arriba del título, con y sin filtro, que lleva al inicio con Proyectos a la vista y que funciona con Tab y Enter. `npm run lint`, `npm test` y `npm run build` en verde.

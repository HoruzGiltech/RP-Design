# Tareas — specs-010: "Volver" en la página de proyectos

> Pasos pequeños y verificables. Se hace **una tarea a la vez** y se marca `[x]` solo cuando se cumple su **verificación**.

**Leyenda:** `[ ]` pendiente · `[x]` hecha · `[~]` en progreso · `[!]` bloqueada (anota el motivo)

Las tareas llevan el prefijo `S10-`. Es un solo bloque, con una pausa ✋ al final.

---

## Fase A — Especificación

- [x] **S10-A1** Crear `specs/specs-010/requirements.md`, `design.md` y `tasks.md`.
- [x] **S10-A2** ✋ **Aprobación** del plan, incluidas P-67 a P-69. (Aprobado el 2026-10-14.)

## Bloque 1 — Frontend

- [x] **S10-B1** Enlace "← Volver" en `ProjectsPage.jsx` y sus estilos. *(RF-67)*
- [x] **S10-B2** `npm run lint`, `npm test` y `npm run build` en verde.
- [x] **S10-B3** Prueba con Playwright en escritorio y celular, con y sin filtro, y con teclado. *(CA-67.1 a CA-67.3)* (1440×900 y 390×844: blanco, 44 px de alto, 16 px sobre el título, sin barra horizontal; el clic y Tab + Enter llevan a `/#proyectos` con la sección a la vista.)
- [x] **S10-B4** ✋ **Prueba del desarrollador.** (Aprobada el 2026-10-14.)

## Fase C — Publicación y cierre

- [x] **S10-C1** Push y comprobación en `rpdesignve.com` (solo Vercel; el backend no cambia). (2026-10-14: Vercel lo publicó en ~20 s.)
- [x] **S10-C2** Actualizar `AGENTS.md` (RF-67, paquete cerrado).

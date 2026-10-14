# Tareas — specs-009: fondo de la sección Proyectos

> Pasos pequeños y verificables. Se hace **una tarea a la vez** y se marca `[x]` solo cuando se cumple su **verificación**.

**Leyenda:** `[ ]` pendiente · `[x]` hecha · `[~]` en progreso · `[!]` bloqueada (anota el motivo)

Las tareas llevan el prefijo `S9-`. Se entrega **por bloques**, con una pausa ✋ al final de cada uno.

---

## Fase A — Especificación

- [x] **S9-A1** Preguntas al desarrollador (P-61 a P-63).
- [x] **S9-A2** Crear `specs/specs-009/requirements.md`, `design.md` y `tasks.md`.
- [x] **S9-A3** ✋ **Aprobación** del plan, incluidas las propuestas P-64 a P-66. (Aprobado el 2026-10-14.)

---

## Bloque 1 — Backend

- [x] **S9-B1** Campos nuevos en `ProjectsSection`, optimización de la imagen al guardar y migración `0021`. *(RF-65, RF-66)*
- [x] **S9-B2** Serializer con los archivos en `null` si la casilla está desmarcada, con tests. *(CA-66.1)*
- [x] **S9-B3** Comprobar en el panel local que los campos aparecen en Proyectos (encabezado) y que la revisión de archivos funciona. (Probado con Playwright: subida de foto y video, el navegador rechaza un `.txt` y el servidor un `.mp4` falso.)
- [x] **S9-B4** ✋ **Prueba del bloque 1.** (Aprobada el 2026-10-14.)

## Bloque 2 — Frontend

- [x] **S9-C1** `pickProjectsBackground` (`utils/projectsBackground.js`), `ProjectsBackground` en `ProjectsTeaser.jsx` y la propiedad `background` de `Section`, con video, imagen y "reducir movimiento". *(CA-65.1, CA-65.2, CA-65.5)*
- [x] **S9-C2** CSS: fondo a todo el ancho, capa oscura y alto en escritorio y celular. *(CA-65.4)*
- [x] **S9-C3** Tests de Vitest (8 de `pickProjectsBackground`; sin librería de componentes, ver `design.md` §3.2). `npm run lint`, `npm test`, `npm run build` y `manage.py test` en verde.
- [x] **S9-C4** Prueba en el navegador (escritorio y celular): con imagen, con video, sin archivos y con la casilla desmarcada. *(CA-65.3, CA-66.2)* (Playwright, 1440×900 y 390×844: el video se reproduce sin sonido; con "reducir movimiento" sale la imagen con su alt; la sección mide 60 % y 50 % de la pantalla; sin barra horizontal; desmarcada o sin archivos queda como antes y no descarga nada. La capa se oscureció a la derecha para que el enlace de Instagram se lea sobre fotos claras.)
- [ ] **S9-C5** ✋ **Prueba del desarrollador.**

## Fase D — Publicación y cierre

- [ ] **S9-D1** Push. Railway aplica la migración al arrancar y Vercel construye el sitio. Comprobar en `rpdesignve.com`.
- [ ] **S9-D2** Actualizar `AGENTS.md` (RF-65 y RF-66, paquete cerrado).

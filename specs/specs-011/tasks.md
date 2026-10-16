# Tareas — specs-011: video de fondo en la sección Proceso

> Pasos pequeños y verificables. Se hace **una tarea a la vez** y se marca `[x]` solo cuando se cumple su **verificación**.

**Leyenda:** `[ ]` pendiente · `[x]` hecha · `[~]` en progreso · `[!]` bloqueada (anota el motivo)

Las tareas llevan el prefijo `S11-`. Son dos bloques, con una pausa ✋ al final de cada uno.

---

## Fase A — Especificación

- [x] **S11-A1** Crear `specs/specs-011/requirements.md`, `design.md` y `tasks.md`.
- [x] **S11-A2** ✋ **Aprobación** del plan, incluidas P-70 a P-74. (Aprobado el 2026-10-16.)

## Bloque 1 — Backend

- [x] **S11-B1** Nombres y ayudas nuevos de los campos del video en `ProcessSection`, y migración `0022`. *(RF-68)*
- [x] **S11-B2** `ProcessSectionSerializer` devuelve `null` en `video` y `video_poster` con la casilla desmarcada, con sus tests.
- [x] **S11-B3** `manage.py test` en verde. (324 tests.)
- [x] **S11-B4** ✋ **Prueba del desarrollador** (el panel muestra los textos nuevos y la API responde bien). Se junta con S11-C6: el desarrollador pidió validar todo en local de una vez. (Aprobada el 2026-10-16.)

## Bloque 2 — Frontend

- [x] **S11-C1** `utils/sectionBackground.js` con `pickSectionBackground`, `pickProjectsBackground` y `pickProcessBackground`, y sus tests.
- [x] **S11-C2** `components/ui/SectionBackground.jsx`, usado por `ProjectsTeaser` (sin cambios visibles en Proyectos).
- [x] **S11-C3** `Process.jsx` y `Process.css`: video de fondo sin controles, texto y tarjetas sobre oscuro. *(RF-68, RF-69)*
- [x] **S11-C4** `npm run lint`, `npm test` y `npm run build` en verde. (33 tests.)
- [x] **S11-C5** Prueba con Playwright en escritorio y celular: el video cubre la sección y arranca solo, sin sonido ni controles; con la casilla desmarcada se ve como antes; con "reducir movimiento" se ve la imagen fija; Proyectos sigue igual. *(CA-68.1 a CA-69.4)* (1440×900 y 390×844: el video mide lo mismo que la sección, `paused=false`, `muted`, `loop`, sin `controls`, sin barra horizontal; con "reducir movimiento" queda la vista previa como `<img>`; con la casilla desmarcada la API manda `null` y la sección vuelve a clara.)
- [x] **S11-C6** ✋ **Prueba del desarrollador.** (Aprobada el 2026-10-16.)

## Fase D — Publicación y cierre

- [x] **S11-D1** Push y comprobación en `rpdesignve.com` (Vercel y Railway, con la migración aplicada), incluida una prueba en un celular real. (2026-10-16: Vercel publicó el sitio; la API de producción ya trae el video con la casilla marcada; en escritorio el video cubre la sección, se reproduce solo, en silencio y sin controles. La prueba en un celular real queda para el desarrollador.)
- [x] **S11-D2** Actualizar `AGENTS.md` (RF-68 y RF-69, paquete cerrado).

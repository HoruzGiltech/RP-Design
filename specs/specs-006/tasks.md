# Tareas — specs-006: publicación temporal (demo)

> Pasos pequeños y verificables. Se hace **una tarea a la vez** y se marca `[x]` solo cuando se cumple su **verificación**.

**Leyenda:** `[ ]` pendiente · `[x]` hecha · `[~]` en progreso · `[!]` bloqueada (anota el motivo)

Las tareas llevan el prefijo `S6-`. Se entrega **por bloques**, con una pausa ✋ al final de cada uno.

---

## Fase A — Especificación

- [x] **S6-A1** Plan y preguntas al desarrollador (P-48 a P-51).
- [x] **S6-A2** Crear `specs/specs-006/requirements.md`, `design.md` y `tasks.md`.
- [x] **S6-A3** Actualizar `AGENTS.md`: specs-006 es el trabajo en curso; el despliegue definitivo sigue pendiente.
- [x] **S6-A4** ✋ **Aprobación** del plan. (Aprobado el 2026-10-13.)

---

## Bloque 1 — Backend listo para producción

- [x] **S6-B1** `gunicorn`, comando de producción en el `Dockerfile` y comando de desarrollo en `docker-compose.yml`. *(RF-49, CA-49.2)*
- [x] **S6-B2** `SERVE_MEDIA` y la vista `serve_media`, con tests. *(RF-50, CA-50.1, CA-50.2)*
- [x] **S6-B3** `NUM_PROXIES`, `get_client_ip` y su uso en los límites y en el bloqueo del panel, con tests. *(RF-51, CA-51.1, CA-51.2)*
- [x] **S6-B4** Prueba en local de la imagen de producción con `DJANGO_DEBUG=False`: panel con estilos, API y una foto. *(CA-49.1)*
- [ ] **S6-B5** ✋ **Prueba del bloque 1.**

---

## Bloque 2 — Frontend y guía

- [x] **S6-C1** `frontend/vercel.json` y la etiqueta `robots` por variable. *(RF-52, RF-53)*
- [x] **S6-C2** `docs/despliegue-demo.md`: Railway, Vercel, variables, copia del contenido, usuarios y comprobaciones. *(RF-55)*
- [ ] **S6-C3** ✋ **Prueba del bloque 2:** el desarrollador lee la guía antes de publicar.

---

## Bloque 3 — Publicación

- [ ] **S6-D1** El desarrollador crea los servicios en Railway y el proyecto en Vercel siguiendo la guía. *(CA-55.1)*
- [ ] **S6-D2** Copia de los datos y de los archivos; usuarios del panel. *(RF-54, CA-54.1, CA-54.2)*
- [ ] **S6-D3** Prueba del sitio publicado: inicio, proyectos, recarga de una dirección interna, formulario con envío real, panel y etiqueta `robots`. *(CA-52.1, CA-53.1)*
- [ ] **S6-D4** ✋ **Aprobación final** y enlace para el cliente.

---

## Fase E — Cierre

- [ ] **S6-E1** Actualizar `docs/problemas-frecuentes.md` con los errores que aparezcan al publicar.
- [ ] **S6-E2** Anotar en `specs/tasks.md` (Fase 5) qué quedó adelantado por esta demo.

---

## Después de specs-006: despliegue definitivo

> ⚠️ **Sigue pendiente.** `specs/tasks.md`, Fase 5: dominio, Cloudflare Pages, R2 (con su código), dominios propios, lista de seguridad completa, Lighthouse y guía del panel para el cliente. Ver `requirements.md` §6.

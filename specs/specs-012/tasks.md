# Tareas — specs-012: sitemap dinámico para Google

**Leyenda:** `[ ]` pendiente · `[x]` hecha · `[~]` en progreso · `[!]` bloqueada

Las tareas llevan el prefijo `S12-`.

## Fase A — Especificación

- [x] **S12-A1** Crear `specs/specs-012/requirements.md`, `design.md` y `tasks.md`.
- [x] **S12-A2** ✋ **Aprobación** del plan y respuesta a P-71.

## Bloque 1 — Backend

- [x] **S12-B1** Vista `/sitemap.xml` con páginas fijas y proyectos publicados. *(RF-71)*
- [x] **S12-B2** Cabecera `X-Robots-Tag: noindex` fuera del sitemap. *(RF-73)*
- [ ] **S12-B3** Tests (publicado, borrador, URLs absolutas, XML, cabeceras) y `manage.py test` en verde.

## Bloque 2 — Frontend

- [x] **S12-C1** Regla en `vercel.json`, `public/robots.txt` y borrar `public/sitemap.xml`. *(RF-72, RF-73)*
- [ ] **S12-C2** `npm run lint`, `npm test` y `npm run build` en verde.

## Fase D — Publicación y cierre

- [ ] **S12-D1** Push (Railway y Vercel) y comprobar `rpdesignve.com/sitemap.xml` y `/robots.txt`. *(CA-72.1, CA-73.1)*
- [x] **S12-D2** Confirmar que `VITE_ROBOTS` no sea `noindex` en producción. (El sitio en vivo ya trae `index, follow`.)
- [ ] **S12-D3** Enviar el sitemap en Search Console y verificar "Correcto". *(CA-72.2)*
- [ ] **S12-D4** Actualizar `AGENTS.md` (RF-71 a RF-73, paquete cerrado).

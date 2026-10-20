# Requisitos — specs-012: sitemap dinámico para Google

> **Qué** se construye. Décimo paquete de cambios.

**Estado:** Pendiente de aprobación

**Reglas:** las mismas de `AGENTS.md`. Este paquete solo describe lo que cambia; lo demás sigue como en `specs/` y en los paquetes anteriores.

---

## 1. Resumen

| # | Pedido | Requisito |
|---|---|---|
| 1 | El sitemap debe actualizarse solo cuando el cliente publica o despublica un proyecto, sin editar archivos ni redesplegar | RF-71 |
| 2 | El sitemap debe estar en `https://rpdesignve.com/sitemap.xml` (mismo dominio que el sitio) para registrarlo en Google Search Console | RF-72 |
| 3 | Que Google encuentre el sitemap y pueda rastrear el sitio | RF-73 |

---

## 2. Requisitos funcionales

### RF-71 — Sitemap generado por el backend

- El backend responde un XML (`application/xml`) con:
  - Páginas fijas: `/`, `/proyectos`, `/terminos`, `/privacidad`.
  - Un `<url>` por cada **proyecto publicado**: `/proyectos/<slug>`.
- Los proyectos en borrador **no** aparecen.
- Cada proyecto lleva `<lastmod>` con su fecha de última modificación (formato `AAAA-MM-DD`). Las páginas fijas no llevan `lastmod` (no hay una fecha real que declarar; Google ignora fechas inventadas).
- No se usan `<priority>` ni `<changefreq>`: Google los ignora.
- La base de las URLs sale de la variable `FRONTEND_URL` del `.env` (ningún dominio escrito en el código).
- Sin librerías nuevas: se usa Django (`django.contrib.sitemaps` o una vista simple).

**Criterios de aceptación**
- [ ] CA-71.1 Publicar un proyecto en el panel lo agrega al sitemap al recargar, sin redeploy.
- [ ] CA-71.2 Despublicarlo o borrarlo lo quita.
- [ ] CA-71.3 Un proyecto en borrador nunca aparece.
- [ ] CA-71.4 Las URLs son absolutas, usan `FRONTEND_URL` y no llevan doble barra.

### RF-72 — Misma dirección que el sitio

- `https://rpdesignve.com/sitemap.xml` muestra el sitemap del backend (reescritura externa en `frontend/vercel.json`, antes del comodín que manda todo a `index.html`). La URL no cambia en el navegador.
- Se elimina el archivo estático `frontend/public/sitemap.xml` para que no haya dos versiones.

**Criterios de aceptación**
- [ ] CA-72.1 `https://rpdesignve.com/sitemap.xml` devuelve XML (no la página del sitio).
- [ ] CA-72.2 Search Console lo acepta con estado "Correcto".

### RF-73 — `robots.txt` y backend fuera del índice

- `https://rpdesignve.com/robots.txt` existe y devuelve texto plano (hoy Vercel devuelve el `index.html`, que Google trata como error).
- Permite el rastreo de todo el sitio y declara `Sitemap: https://rpdesignve.com/sitemap.xml`.
- El panel y la API (`api.rpdesignve.com`) no se indexan: el backend agrega la cabecera `X-Robots-Tag: noindex` a todas sus respuestas, excepto a `/sitemap.xml`.

**Criterios de aceptación**
- [ ] CA-73.1 `/robots.txt` responde `text/plain` con la línea `Sitemap:`.
- [ ] CA-73.2 El panel y la API responden con `X-Robots-Tag: noindex`.

---

## 3. Lo que no cambia

- Las rutas, páginas y la API pública del sitio.
- La etiqueta `robots` del `index.html` (`VITE_ROBOTS`): hay que confirmar que en Vercel producción no diga `noindex` (ver P-71).

## 4. Preguntas para el desarrollador

- **P-71.** ¿Confirmas que `VITE_ROBOTS` en Vercel (producción) está en `index, follow`? Si dice `noindex`, Google ignora el sitemap y no indexa nada.

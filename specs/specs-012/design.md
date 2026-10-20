# Diseño — specs-012: sitemap dinámico para Google

> **Cómo** se construye. Solo lo que cambia.

## 1. Backend

- Nueva vista `sitemap_xml` (en `backend/projects/views.py`, o `django.contrib.sitemaps`; se elige la más simple al implementar), publicada en `config/urls.py` como `path("sitemap.xml", ...)`, fuera de `api/`.
- Datos: los proyectos publicados, con el mismo filtro que usa la API pública, tomando `slug` y la fecha de modificación.
- Base de URLs: `settings.FRONTEND_URL.rstrip("/")`.
- Respuesta: `Content-Type: application/xml; charset=utf-8`, con `Cache-Control: public, max-age=3600` para no golpear la base en cada visita de un rastreador.
- Solo lectura, sin autenticación, solo `GET`.

## 2. Frontend (Vercel)

`frontend/vercel.json`, con la regla del sitemap **antes** del comodín:

```json
{
  "rewrites": [
    { "source": "/sitemap.xml", "destination": "https://api.rpdesignve.com/sitemap.xml" },
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

`frontend/public/robots.txt` (Vite lo copia a la raíz):

```
User-agent: *
Allow: /

Sitemap: https://rpdesignve.com/sitemap.xml
```

Se borra `frontend/public/sitemap.xml`.

## 3. Panel y API fuera del índice

Un middleware simple en Django agrega `X-Robots-Tag: noindex` a todas las respuestas menos `/sitemap.xml` y `/media/` (si no, las fotos de los proyectos no saldrían en Google Imágenes). Requiere `FRONTEND_URL=https://rpdesignve.com` en Railway. Así `api.rpdesignve.com` no compite en Google con el sitio.

## 4. Tests

- Un proyecto publicado aparece; un borrador no.
- Las URLs son absolutas y salen de `FRONTEND_URL`.
- El tipo de contenido es XML y el XML es válido.
- `X-Robots-Tag: noindex` está en la API y no en el sitemap.

## 5. Decisiones y riesgos

| Tema | Decisión / riesgo |
|---|---|
| Dominio del sitemap | Debe verse en `rpdesignve.com`; por eso la reescritura de Vercel y no registrar la URL del subdominio `api` |
| `lastmod` | Solo en proyectos, con su fecha real |
| `noindex` en producción | **Riesgo principal.** Si `VITE_ROBOTS` de Vercel dice `noindex`, no se indexará nada. Se comprueba antes de enviar el sitemap |
| Sitio SPA | Google ejecuta JavaScript y debería leer los textos, pero tarda más que con HTML ya armado. Posible mejora futura, fuera de este paquete: prerender de las páginas |
| Título y descripción por página | Ya los pone el sitio con los datos de SEO; se verifica con "Inspección de URL" en Search Console |

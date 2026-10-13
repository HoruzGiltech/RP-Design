# Requisitos — specs-006: publicación temporal (demo) en Vercel y Railway

> **Qué** hace falta para que el cliente vea el sitio en internet y **cómo sabemos que está bien hecho**.
> No cambia nada de lo que el visitante ve: prepara el proyecto para ejecutarse fuera de la computadora del desarrollador.

**Estado:** Aprobado (v1, 2026-10-13) — plan aprobado por el desarrollador; se implementa por bloques
**Base:** `specs/` y los paquetes `specs-001` a `specs-005`, implementados y cerrados.
**Reglas:** las mismas de `AGENTS.md`. En especial §6 (Seguridad): ninguna clave va al repositorio.

> ⚠️ **Esto NO es el despliegue definitivo.** El de `specs/tasks.md`, Fase 5 (dominio propio, Cloudflare Pages y R2) **sigue pendiente**. Esta demo adelanta parte de ese trabajo; qué queda después está en §6.

---

## 1. Resumen

| # | Necesidad | Requisito |
|---|---|---|
| 1 | El backend debe arrancar con un servidor de producción | RF-49 |
| 2 | Las fotos y videos se guardan en un volumen y hay que servirlos | RF-50 |
| 3 | Detrás del proxy, los límites deben contar por visitante, no todos juntos | RF-51 |
| 4 | El sitio en Vercel debe abrir cualquier dirección interna | RF-52 |
| 5 | La demo no debe aparecer en buscadores | RF-53 |
| 6 | La demo arranca con el contenido que hay en local | RF-54 |
| 7 | El desarrollador publica siguiendo una guía | RF-55 |

**Dónde queda cada pieza**

| Pieza | Dónde |
|---|---|
| Sitio (React) | Vercel (`*.vercel.app`) |
| Backend y panel (Django) | Railway (`*.up.railway.app`) |
| Base de datos | Postgres de Railway |
| Fotos, videos y fuentes | Volumen de Railway, servidos por Django |

---

## 2. Requisitos funcionales

### RF-49 — Backend con servidor de producción

1. La imagen del backend arranca con `gunicorn`, en el puerto que indique la plataforma (`PORT`).
2. Antes de arrancar aplica las migraciones y reúne los archivos estáticos del panel.
3. En local nada cambia: `docker compose up` sigue usando el servidor de desarrollo, con recarga automática.

**Criterios de aceptación**
- [ ] CA-49.1 En local, con `DJANGO_DEBUG=False` y la imagen de producción, el panel carga con sus estilos y la API responde.
- [ ] CA-49.2 `docker compose up` sigue funcionando como antes.

### RF-50 — Archivos subidos servidos desde el volumen

1. Con la variable `SERVE_MEDIA=True`, Django sirve los archivos de `media/` también con `DJANGO_DEBUG=False`.
2. Sin esa variable, en producción no los sirve (así queda listo para R2, donde los sirve Cloudflare).
3. En local se siguen sirviendo como hoy.

**Criterios de aceptación**
- [ ] CA-50.1 Con `SERVE_MEDIA=True` una foto subida se descarga por su dirección; con `False`, responde 404.
- [ ] CA-50.2 No se puede salir de la carpeta `media/` con una dirección manipulada.

### RF-51 — La dirección IP real del visitante

1. La variable `NUM_PROXIES` dice cuántos proxies hay delante del backend (0 en local, 1 en Railway).
2. El límite de la API, el de cotizaciones (5 por hora) y el bloqueo del panel por intentos fallidos cuentan por la IP real del visitante.
3. Con `NUM_PROXIES=0` se ignora la cabecera `X-Forwarded-For`: nadie puede saltarse un límite inventándola.

**Criterios de aceptación**
- [ ] CA-51.1 Con `NUM_PROXIES=1`, dos visitantes distintos detrás del mismo proxy tienen cada uno su propio límite.
- [ ] CA-51.2 Con `NUM_PROXIES=0`, cambiar `X-Forwarded-For` no evita el límite.

### RF-52 — Sitio en Vercel

1. Cualquier dirección del sitio (`/proyectos`, `/proyectos/<slug>`, `/privacidad`) abre también al recargar o al entrar desde un enlace compartido.
2. La dirección de la API sale de `VITE_API_URL`, configurada en Vercel.

**Criterios de aceptación**
- [ ] CA-52.1 Recargar `/proyectos/<slug>` en el sitio publicado muestra el proyecto, no un error 404.

### RF-53 — La demo no se indexa

1. Con `VITE_ROBOTS=noindex, nofollow` el sitio le pide a los buscadores que no lo indexen.
2. Por defecto (sin la variable de la demo) el valor es `index, follow`: el sitio definitivo sí se indexa.

**Criterios de aceptación**
- [ ] CA-53.1 El HTML publicado en Vercel trae `<meta name="robots" content="noindex, nofollow">`.

### RF-54 — Contenido inicial

1. La demo arranca con el contenido de la computadora del desarrollador: proyectos, categorías, servicios, pasos, áreas y precios, textos y configuración, con sus fotos y videos.
2. **No** se copian las cotizaciones, los usuarios, las sesiones ni los registros de intentos de acceso.
3. Los usuarios del panel se crean en la demo con contraseñas nuevas.

**Criterios de aceptación**
- [ ] CA-54.1 El sitio publicado muestra los mismos proyectos y servicios que el local, con sus imágenes.
- [ ] CA-54.2 El panel publicado no tiene ninguna cotización de prueba.

### RF-55 — Guía de publicación

1. `docs/despliegue-demo.md` explica paso a paso cómo publicar: qué crear en Railway y en Vercel, cada variable con su valor o cómo generarlo, y cómo comprobar que quedó bien.
2. Incluye cómo copiar el contenido, cómo crear los usuarios y qué hacer si algo falla.
3. Ninguna clave real aparece en la guía ni en el repositorio.

**Criterios de aceptación**
- [ ] CA-55.1 El desarrollador publica la demo siguiendo solo la guía.

---

## 3. Seguridad de la demo

- `DJANGO_DEBUG=False`, con una `DJANGO_SECRET_KEY` nueva (el backend se niega a arrancar con la de ejemplo).
- `DJANGO_ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS` y `CSRF_TRUSTED_ORIGINS` con las direcciones exactas de Railway y Vercel.
- Panel en una dirección distinta de `/admin/`, con contraseñas nuevas y largas.
- HTTPS obligatorio y cookies seguras (ya lo hace el código con `DJANGO_DEBUG=False`).

---

## 4. Decisiones confirmadas

| # | Tema | Decisión |
|---|---|---|
| P-48 | Cuentas | El desarrollador ya tiene Vercel y Railway |
| P-49 | Archivos subidos | Volumen de Railway, servidos por Django. R2 queda para el despliegue definitivo |
| P-50 | Contenido inicial | Copia del contenido local, sin cotizaciones ni usuarios |
| P-51 | Quién publica | El desarrollador, con la guía. Las claves no pasan por el agente ni por el repositorio |

---

## 5. Limitaciones aceptadas de la demo

- **Videos en iPhone:** Django no entrega los archivos "por partes", que es como Safari pide los videos. El video de la Portada o de una galería puede no reproducirse en iPhone. Se resuelve con R2.
- **Velocidad:** las fotos salen del mismo servidor que el panel, sin red de distribución.
- **Textos legales:** Términos y Privacidad siguen con `[TEXTO PENDIENTE]`.
- **Vercel gratuito:** su plan Hobby es para uso no comercial.
- **Costo:** Railway cobra por uso (alrededor de USD 5 al mes).
- **WhatsApp real:** las cotizaciones enviadas desde la demo llegan al número de RP Design.

---

## 6. Lo que sigue pendiente para el despliegue definitivo

De `specs/tasks.md`, Fase 5: dominio y DNS en Cloudflare (T-5.1), almacenamiento en R2 con su código (T-5.2), frontend en Cloudflare Pages (T-5.5), dominios propios (T-5.6), lista de seguridad completa (T-5.7), Lighthouse (T-5.8) y guía del panel para el cliente (T-5.9). Los textos legales los entrega el cliente.

De esa fase, esta demo deja adelantado: el servidor de producción (parte de T-5.3), las migraciones y los estáticos al arrancar (parte de T-5.4) y la IP real detrás del proxy (parte de T-5.7).

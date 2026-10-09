# Tareas — specs-003

> Pasos pequeños y verificables. Se hace **una tarea a la vez** y se marca `[x]` solo cuando se cumple su **verificación**.
> Cada tarea indica qué requisito cubre de `specs/specs-003/requirements.md`.

**Leyenda:** `[ ]` pendiente · `[x]` hecha · `[~]` en progreso · `[!]` bloqueada (anota el motivo)

Las tareas llevan el prefijo `S3-` para no confundirlas con las de `specs/tasks.md` ni con las de los paquetes anteriores (`S1-`, `S2-`).

---

## Fase A — Especificación

- [x] **S3-A1** Plan de los 17 cambios, con las preguntas al desarrollador (8 decisiones confirmadas, P-15 a P-22).
- [x] **S3-A2** Crear `specs/specs-003/requirements.md`, `design.md` y `tasks.md`.
- [x] **S3-A3** Actualizar `AGENTS.md`: specs-003 es el trabajo en curso y el despliegue sigue siendo la última fase.
- [x] **S3-A4** ✋ **Aprobación** de specs-003 y de las decisiones P-23 a P-30 (`requirements.md` §5). (Aprobado el 2026-10-09.)

---

## Fase B — Backend

### B1. Categorías y proyectos
- [x] **S3-B1** `ProjectCategory.is_visible`, en el panel y en las dos listas de categorías (`/api/project-categories/` y `/api/quote-categories/`). Una categoría oculta en `?category=` devuelve todos. *(RF-20)*
  - Verificación: tests de CA-20.1 a CA-20.3.
- [x] **S3-B2** `description` en la tarjeta de proyecto de la API. *(RF-22)*

### B2. Contenido del sitio
- [x] **S3-B3** `validate_font_file` y `MAX_FONT_MB`. *(RF-19.3, CA-19.1)*
  - Verificación: tests con cada formato válido, un archivo falso y uno demasiado grande.
- [x] **S3-B4** `SiteSettings`: `heading_font`, `body_font` y `show_estimate`, en el panel y en `/api/site/`. *(RF-19.1, RF-30.1)*
- [x] **S3-B5** `ServicesSection.cta_text`. `Service` y `ProcessStep` con relación a su sección, y sus tablas dentro del formulario de la sección; se quitan sus entradas del menú. *(RF-24.3, RF-25)*
  - Verificación: tests del panel; ningún paso ni servicio se pierde en la migración.
- [x] **S3-B6** Modelo `QuoteFormField`, migración con las 11 filas, tabla dentro de "Contacto" y `form_fields` en `/api/site/`. *(RF-31)*
  - Verificación: tests: no se agregan ni borran filas; la API devuelve las 11 claves.

### B3. Cotización con varias áreas
- [x] **S3-B7** Modelo `QuoteItem` y campos `location`, `has_photos` y `needs_visit` en `Quote`. Migración `quotes.0006`. *(RF-27.7, RF-32)*
- [x] **S3-B8** Migración de datos `quotes.0007`: cada cotización existente pasa a tener un renglón. *(RF-27.8)*
  - Verificación: test que compara una cotización antes y después.
- [x] **S3-B9** Migración `quotes.0008`: se eliminan de `Quote` los campos que pasaron al renglón.
  - Verificación: `makemigrations --check` sin cambios pendientes.
- [x] **S3-B10** `services.py`: `calculate_total` y el mensaje nuevo, sin emojis y con renglones. *(RF-27.3, RF-27.4, RF-28)*
  - Verificación: tests de CA-27.1 y CA-28.1, y de cada línea opcional del mensaje.
- [x] **S3-B11** `POST /api/quotes/` con `items` y los campos nuevos; validación de cada renglón. *(RF-27, RF-32, CA-27.3, CA-27.4, CA-32.1, CA-32.2)*
- [x] **S3-B12** `show_estimate` apagado: respuesta sin monto y mensaje sin estimado, guardando el estimado igual. *(RF-30, CA-30.1, CA-30.2)*
- [x] **S3-B13** Panel de cotizaciones: tabla de renglones, ubicación, fotos y visita. *(RF-27.7, RF-32.4)*
- [x] **S3-B14** Migración `core.0004`: permisos de `QuoteItem` y `QuoteFormField` para Admin y Viewer.
  - Verificación: pasa el test de roles que avisa de permisos olvidados.

- [ ] **S3-B15** ✋ **Revisión de fin de fase:** `manage.py test` completo y demo del panel.

---

## Fase C — Frontend

### C1. Cambios simples
- [x] **S3-C1** Inicio: Proceso antes que Servicios; el menú no cambia. *(RF-23)*
- [x] **S3-C2** `/proyectos` con el título de la sección. *(RF-21)*
- [x] **S3-C3** Pie con los iconos de WhatsApp, correo e Instagram; Contacto sin datos; se borra `ContactInfo`. *(RF-33)*
  - Verificación con Playwright: enlaces, áreas de 44 px y que el botón flotante no tape los iconos a 360 px.
- [x] **S3-C4** Botón "Cotizar" en las tarjetas de Servicios. *(RF-24)*
  - Verificación con Playwright: aparece con mouse y con teclado; la tarjeta no cambia de tamaño.
- [x] **S3-C5** Descripción completa en la capa de las tarjetas de proyecto. *(RF-22)*
  - Verificación con Playwright: descripción larga con scroll; contraste del texto.

### C2. Fuentes y hero
- [x] **S3-C6** `useCustomFonts`. *(RF-19.2, RF-19.5, CA-19.2 a CA-19.4)*
  - Verificación con Playwright: subir una fuente de prueba al panel, ver el cambio y quitarla.
- [x] **S3-C7** Hero: el video como primera portada; `useSlideshow` avanza al terminar el video. *(RF-26)*
  - Verificación con Playwright: video + imágenes, pausa, vuelta al video y movimiento reducido.

### C3. Formulario
- [x] **S3-C8** `utils/estimate.js` (`calculateTotal`) y `utils/quoteValidation.js` con renglones y campos nuevos, con tests en Vitest. *(RF-27, RF-32)*
- [x] **S3-C9** `SquareMetersSlider` con campo numérico y barra sincronizados. *(RF-29)*
- [x] **S3-C10** `AreaItem` y áreas con casillas en `QuoteCalculator`; total como suma. *(RF-27, CA-27.1, CA-27.2)*
- [x] **S3-C11** Campos nuevos: ubicación, "tengo fotos" y "no sé cuántos m²". *(RF-32)*
- [x] **S3-C12** Títulos y textos de ejemplo desde el panel. *(RF-31, CA-31.1, CA-31.2)*
- [x] **S3-C13** Interruptor del estimado en el formulario y en la pantalla de confirmación. *(RF-30)*
- [x] **S3-C14** Prueba completa del formulario con Playwright: dos áreas, m² a mano, suma, visita, envío real y mensaje sin emojis; y con el estimado apagado. *(CA-27.5, CA-28.1, CA-30.1)*

### C4. Revisión
- [x] **S3-C15** Revisión responsive (360, 768, 1280 y 1920 px) y de accesibilidad de todo lo nuevo: teclado en las casillas y los m², contraste, nombres accesibles. *(RNF-12, RNF-13)*

- [ ] **S3-C16** ✋ **Revisión de fin de fase:** `npm test`, `npm run lint` y `npm run build` pasan; demo del sitio y prueba en un celular real (sobre todo, que el mensaje llegue bien a WhatsApp).

---

## Fase D — Cierre

- [x] **S3-D1** Actualizar `docs/problemas-frecuentes.md` si apareció algún error nuevo.
- [ ] **S3-D2** Anotar en `specs/requirements.md`, `specs/design.md` y los paquetes anteriores qué apartados quedaron sustituidos por specs-003.
- [ ] **S3-D3** ✋ Aprobación final.

---

## Después de specs-003: despliegue

> ⚠️ **Sigue pendiente y no se ha empezado.** Las tareas están en `specs/tasks.md`, **Fase 5 (T-5.1 a T-5.9)**.

| Qué | Depende de |
|---|---|
| T-5.1 Dominio y DNS en Cloudflare | Que el cliente compre el dominio |
| T-5.2 Bucket R2 y almacenamiento de archivos | Cuenta de Cloudflare. **El código de R2 todavía no está escrito** (`specs/design.md` §2.11). Ahora también guardará las fuentes |
| T-5.3 y T-5.4 Backend y base de datos en Railway | Cuenta de Railway. Falta la imagen de producción con gunicorn |
| T-5.5 y T-5.6 Frontend en Cloudflare Pages y dominios | Lo anterior |
| T-5.7 Lista de comprobación de seguridad | Incluye leer la IP real detrás del proxy y que no quede ningún `[TEXTO PENDIENTE]` legal |
| T-5.8 Lighthouse | Sitio publicado |
| T-5.9 Guía de uso del panel para el cliente | — |

Lo que se puede adelantar **sin dominio ni cuentas**: almacenamiento en R2 por variables de entorno, lectura de la IP real detrás del proxy, imagen de producción con gunicorn, `README.md` y la guía del panel.

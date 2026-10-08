# Tareas — specs-002

> Pasos pequeños y verificables. Se hace **una tarea a la vez** y se marca `[x]` solo cuando se cumple su **verificación**.
> Cada tarea indica qué requisito cubre de `specs/specs-002/requirements.md`.

**Leyenda:** `[ ]` pendiente · `[x]` hecha · `[~]` en progreso · `[!]` bloqueada (anota el motivo)

Las tareas llevan el prefijo `S2-` para no confundirlas con las de `specs/tasks.md` ni con las de specs-001 (`S1-`).

---

## Fase A — Especificación

- [x] **S2-A1** Crear `specs/specs-002/requirements.md`, `design.md` y `tasks.md`.
- [x] **S2-A2** Actualizar `AGENTS.md`: specs-002 es el trabajo en curso y el despliegue sigue siendo la última fase.
- [x] **S2-A3** ✋ **Aprobación** de specs-002 y de las decisiones P-10 a P-14 (`requirements.md` §5). (Aprobado el 2026-10-07.)

---

## Fase B — Backend

### B1. Áreas por tipo de remodelación
- [x] **S2-B1** `RemodelArea.category`, `Quote.category` y `Quote.category_name`; el identificador del área se genera solo. Migración `quotes.0004`. *(RF-17.3, RF-17.4, RF-17.7)*
  - Verificación: tests: dos áreas con el mismo nombre en categorías distintas reciben identificadores distintos.
- [x] **S2-B2** Migración de datos `quotes.0005`: áreas actuales → Residencial; "Otro" sin categoría; crea Oficina, Sala de reuniones y Showroom. *(RF-17.5)*
  - Verificación: test de que, en una base nueva, cada categoría tiene las áreas de CA-17.1.
- [x] **S2-B3** `services.py`: `area_belongs_to_category` y el tipo en `build_whatsapp_message`. *(RF-17.7, CA-17.6)*
  - Verificación: tests: área propia, ajena y común; mensaje con y sin tipo.
- [x] **S2-B4** `GET /api/quote-categories/` y eliminación de `/api/quote-areas/`. *(RF-17.1, RF-17.2, RF-17.8)*
  - Verificación: tests: agrupa por categoría, "Otro" en todas, respeta el orden, oculta inactivas y categorías sin áreas.
- [x] **S2-B5** `POST /api/quotes/`: `category` obligatorio, validación de que el área pertenece al tipo, y guardado del tipo. *(CA-17.3, CA-17.5)*
  - Verificación: tests: falta el tipo → 400; área de otro tipo → 400; "Otro" con cualquier tipo → 201.
- [x] **S2-B6** Panel: categoría en la lista de áreas (columna, filtro y edición), "Áreas del formulario" en categorías, y tipo en las cotizaciones. *(RF-17.3, RF-17.9)*
  - Verificación: tests del panel y revisión en navegador con Playwright.

### B2. Hero y especialidades
- [x] **S2-B7** `HeroSection.show_primary_cta` y `show_secondary_cta`, en el panel y en `/api/site/`. Migración `site_content.0010`. *(RF-14.1)*
- [x] **S2-B8** "Especialidades": aviso en el panel de que ya no se muestran y `specialties` fuera de `/api/site/`. *(RF-16.2, CA-16.2)*

- [ ] **S2-B9** ✋ **Revisión de fin de fase:** `manage.py test` completo y demo del panel (áreas por categoría, interruptores del hero).

---

## Fase C — Frontend

- [x] **S2-C1** `api/endpoints.js` (`getQuoteCategories`) y `validateQuote` con el tipo, con sus tests en Vitest.
- [x] **S2-C2** Formulario: campo "Tipo de remodelación", áreas según el tipo y reinicio del área al cambiar de tipo. *(RF-17.1, RF-17.2, RF-17.6, CA-17.1, CA-17.4)*
  - Verificación con Playwright: cada tipo ofrece sus áreas; envío real con el tipo en el mensaje.
- [x] **S2-C3** Sección Contacto en una columna: formulario a todo el ancho con sus campos en columnas, y datos de contacto en fila debajo. *(RF-18)*
  - Verificación con Playwright a 360, 768, 1280 y 1920 px; orden de `Tab` igual al visual.
- [x] **S2-C4** Revisar el botón flotante de WhatsApp con la nueva sección Contacto (sigue sin tapar el envío). *(CA-12.3 de specs-001)*
- [x] **S2-C5** Quitar el cintillo: `HomePage` sin `SpecialtiesStrip`; borrar ese componente, `Marquee` y sus tokens. *(RF-16.1, CA-16.1)*
- [x] **S2-C6** Hero: botones según sus interruptores. *(RF-14.2, RF-14.3, CA-14.1)*
  - Verificación con Playwright: los dos, uno y ninguno.
- [x] **S2-C7** Hero: controles discretos con barra de progreso en el indicador activo. *(RF-15)*
  - Verificación con Playwright: mouse y teclado; áreas pulsables de 44 px; pausa detiene el progreso; movimiento reducido.
- [x] **S2-C8** Encabezado: menú siempre desplegable debajo del logo; se cierra al elegir, con `Esc` y al pulsar fuera. *(RF-13.1 a RF-13.4, CA-13.1, CA-13.2)*
- [x] **S2-C9** `useHideOnScroll`: el encabezado se oculta al bajar y vuelve al subir. *(RF-13.5, RF-13.6, CA-13.3 a CA-13.5, RNF-11)*
  - Verificación con Playwright: baja, sube, menú abierto, foco con `Tab` y movimiento reducido.
- [x] **S2-C10** Revisión responsive (360, 768, 1280 y 1920 px) y de accesibilidad de todo lo nuevo.

- [ ] **S2-C11** ✋ **Revisión de fin de fase:** `npm test`, `npm run lint` y `npm run build` pasan; demo del sitio y prueba en un celular real.

---

## Fase D — Cierre

- [x] **S2-D1** Actualizar `docs/problemas-frecuentes.md` si apareció algún error nuevo.
- [x] **S2-D2** Anotar en `specs/requirements.md`, `specs/design.md` y `specs/specs-001/` qué apartados quedaron sustituidos por specs-002.
- [ ] **S2-D3** ✋ Aprobación final.

---

## Después de specs-002: despliegue

> ⚠️ **Sigue pendiente y no se ha empezado.** Las tareas están en `specs/tasks.md`, **Fase 5 (T-5.1 a T-5.9)**.

| Qué | Depende de |
|---|---|
| T-5.1 Dominio y DNS en Cloudflare | Que el cliente compre el dominio |
| T-5.2 Bucket R2 y almacenamiento de archivos | Cuenta de Cloudflare. **El código de R2 todavía no está escrito** (`design.md` §2.11) |
| T-5.3 y T-5.4 Backend y base de datos en Railway | Cuenta de Railway. Falta la imagen de producción con gunicorn |
| T-5.5 y T-5.6 Frontend en Cloudflare Pages y dominios | Lo anterior |
| T-5.7 Lista de comprobación de seguridad | Incluye leer la IP real detrás del proxy (límite de envíos y bloqueo del login) y que no quede ningún `[TEXTO PENDIENTE]` legal |
| T-5.8 Lighthouse | Sitio publicado |
| T-5.9 Guía de uso del panel para el cliente | — |

Lo que se puede adelantar **sin dominio ni cuentas**: almacenamiento en R2 por variables de entorno, lectura de la IP real detrás del proxy, imagen de producción con gunicorn, `README.md` y la guía del panel.

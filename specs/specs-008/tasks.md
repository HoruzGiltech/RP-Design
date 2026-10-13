# Tareas — specs-008

> Pasos pequeños y verificables. Se marca `[x]` solo cuando se cumple su **verificación**.

**Leyenda:** `[ ]` pendiente · `[x]` hecha · `[~]` en progreso · `[!]` bloqueada

Prefijo `S8-`. Se entrega por bloques, con una pausa ✋ al final de cada uno.

---

## Fase A — Especificación

- [x] **S8-A1** Plan, preguntas (P-55 a P-57) y referencia visual del desarrollador.
- [x] **S8-A2** Crear `specs/specs-008/` y actualizar `AGENTS.md`.
- [x] **S8-A3** ✋ Aprobación del plan (2026-10-13; el fondo de Proyectos se queda en negro).

---

## Bloque 1 — Formulario

- [x] **S8-B1** `Quote.remodel_type` y `Quote.square_meters`; migración `quotes.0009`. *(RF-61, RF-62)*
- [x] **S8-B2** Mensaje de WhatsApp nuevo y limpieza de las reglas de precio. *(RF-63.1, RF-63.2)*
- [x] **S8-B3** `POST /api/quotes/` con el formato nuevo; se elimina `/api/quote-categories/`. Con tests. *(RF-61 a RF-63, CA-63.3)*
- [x] **S8-B4** Campos del formulario: migraciones `site_content.0016` y `0017`. *(RF-61.2)*
- [x] **S8-B5** Panel: cotizaciones con los campos nuevos; se retiran "Áreas y precios" y el bloque "Calculadora". *(RF-63.3, RF-63.4, CA-63.1, CA-63.2)*
- [x] **S8-B6** Frontend: formulario nuevo y limpieza de componentes y utilidades. *(RF-61 a RF-63, CA-62.1, CA-62.2)*
- [x] **S8-B7** Prueba en el navegador con envío real y revisión a 360, 768 y 1280 px.
- [x] **S8-B8** ✋ **Prueba del bloque 1.** (El desarrollador pidió el campo de m² numérico con el ejemplo "10 m²" y, hecho eso, continuar: 2026-10-13.)

---

## Bloque 2 — Secciones del inicio

- [x] **S8-C1** `ProcessSection.intro` y `show_video`; migración de los títulos. *(RF-58.3, RF-59, RF-60.3)*
- [x] **S8-C2** Proceso en tarjetas numeradas, con el video según la casilla. *(RF-58, RF-59, CA-58.1, CA-58.2, CA-59.1)*
- [x] **S8-C3** Servicios sin números. *(RF-60, CA-60.1, CA-60.2)*
- [x] **S8-C4** Revisión responsive y de accesibilidad.
- [ ] **S8-C5** ✋ **Prueba del bloque 2.**

---

## Cierre

- [ ] **S8-D1** Anotar en `specs/` y en los paquetes anteriores qué quedó sustituido.
- [ ] **S8-D2** ✋ Aprobación final y subida a la demo.

---

> ⚠️ Siguen pendientes: terminar `specs/specs-006/` (usuarios del panel de la demo y comprobaciones finales) y el **despliegue definitivo** (`specs/tasks.md`, Fase 5).

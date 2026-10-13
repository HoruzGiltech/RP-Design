# Tareas — specs-007

> Pasos pequeños y verificables. Se marca `[x]` solo cuando se cumple su **verificación**.

**Leyenda:** `[ ]` pendiente · `[x]` hecha · `[~]` en progreso · `[!]` bloqueada

Prefijo `S7-`. Es un paquete pequeño: un solo bloque, con su pausa de prueba.

---

- [x] **S7-A1** Propuesta al desarrollador y aprobación (2026-10-13).
- [x] **S7-A2** Crear `specs/specs-007/` y actualizar `AGENTS.md`.

## Bloque único

- [x] **S7-B1** `get_upload_rules` en `core/validators.py`, con tests. *(RF-56.4)*
- [x] **S7-B2** `FileCheckMixin` y su uso en los formularios del panel con archivos, con tests. *(RF-56.5)*
- [x] **S7-B3** `admin-file-check.js`. *(RF-56.1 a RF-56.3)*
- [x] **S7-B4** Texto alternativo automático en galería, portada y servicios; migración `projects.0007`; tests. *(RF-57)*
- [ ] **S7-B5** Prueba en el navegador con Playwright: archivo pesado, formato no permitido, video, fila nueva de galería y guardado sin textos alternativos. *(CA-56.1 a CA-56.3, CA-57.1)*
- [ ] **S7-B6** ✋ **Prueba del desarrollador** en local.
- [ ] **S7-B7** Subir a GitHub para que llegue a la demo y comprobarlo ahí.

## Cierre

- [ ] **S7-C1** Anotar en `specs/requirements.md` que el texto alternativo ya no es obligatorio.
- [ ] **S7-C2** ✋ Aprobación final.

---

> ⚠️ Sigue pendiente: terminar `specs/specs-006/` (usuarios del panel de la demo y comprobaciones finales) y el **despliegue definitivo** (`specs/tasks.md`, Fase 5).

# Tareas — specs-005

> Pasos pequeños y verificables. Se hace **una tarea a la vez** y se marca `[x]` solo cuando se cumple su **verificación**.
> Cada tarea indica qué requisito cubre de `specs/specs-005/requirements.md`.

**Leyenda:** `[ ]` pendiente · `[x]` hecha · `[~]` en progreso · `[!]` bloqueada (anota el motivo)

Las tareas llevan el prefijo `S5-`. El paquete se entrega **por bloques**: cada uno se guarda como commit local y termina en una pausa ✋ para que el desarrollador lo pruebe.

---

## Fase A — Especificación

- [x] **S5-A1** Plan de los cambios, con las preguntas al desarrollador (P-42 a P-46).
- [x] **S5-A2** Crear `specs/specs-005/requirements.md`, `design.md` y `tasks.md`.
- [x] **S5-A3** Actualizar `AGENTS.md`: specs-005 es el trabajo en curso y el despliegue sigue siendo la última fase.
- [x] **S5-A4** ✋ **Aprobación** del plan. (Aprobado el 2026-10-09, con Ubicación obligatoria.)

---

## Bloque 1 — Formulario y cuadrícula de Servicios

- [ ] **S5-B1** El formulario ofrece y acepta todas las categorías, también las ocultas; nueva ayuda de la casilla (migración `projects.0006`). Con tests. *(RF-42, CA-42.1, CA-42.2)*
- [ ] **S5-B2** "Ubicación del espacio" obligatoria en el backend y en el navegador, con tests. *(RF-43, CA-43.1)*
- [ ] **S5-B3** Servicios con hasta 4 tarjetas por fila. *(RF-44, CA-44.1, CA-44.2)*
- [ ] **S5-B4** ✋ **Prueba del bloque 1.**

---

## Bloque 2 — Capas en celular y detalle del proyecto

- [ ] **S5-C1** Hook `useInCenter` y regla `is-centered` en `overlay.css`; se quita la capa fija de specs-004. *(RF-46)*
- [ ] **S5-C2** Tarjetas de servicio y de proyecto con la capa al centrarse; el texto de las tarjetas de proyecto queda fijo. *(RF-46, CA-46.1 a CA-46.3)*
- [ ] **S5-C3** Detalle: se quita la descripción de debajo; la capa es accesible con teclado y lector de pantalla, y en celular aparece al centrarse. *(RF-45, CA-45.1, CA-45.2)*
- [ ] **S5-C4** ✋ **Prueba del bloque 2**, en computadora y en celular.

---

## Bloque 3 — Animaciones en móvil y encabezado

- [ ] **S5-D1** Medir las entradas en emulación de Android y anotar la causa en `design.md` §3.4. *(RF-47)*
- [ ] **S5-D2** Ajustar las entradas según la medición. *(RF-47, CA-47.1)*
- [ ] **S5-D3** Reproducir y corregir el encabezado que se queda fijo; anotar la causa en `design.md` §3.5. *(RF-48, CA-48.1)*
- [ ] **S5-D4** Revisión responsive (360, 768, 1280 y 1920 px) y de accesibilidad de todo el paquete. *(RNF-20)*
- [ ] **S5-D5** ✋ **Prueba del bloque 3:** `manage.py test`, `npm test`, `npm run lint` y `npm run build` pasan; el desarrollador lo revisa en su Android. *(CA-47.2)*

---

## Fase E — Cierre

- [ ] **S5-E1** Actualizar `docs/problemas-frecuentes.md` si apareció algún error nuevo.
- [ ] **S5-E2** Anotar en `specs/` y en los paquetes anteriores qué apartados quedaron sustituidos por specs-005.
- [ ] **S5-E3** ✋ Aprobación final.

---

## Después de specs-005: despliegue

> ⚠️ **Sigue pendiente y no se ha empezado.** Las tareas están en `specs/tasks.md`, **Fase 5 (T-5.1 a T-5.9)**: dominio y DNS, almacenamiento en R2 (el código todavía no está escrito), backend y base de datos en Railway (falta la imagen de producción con gunicorn), frontend en Cloudflare Pages, lista de seguridad, Lighthouse y guía del panel.

Lo que se puede adelantar **sin dominio ni cuentas**: almacenamiento en R2 por variables de entorno, lectura de la IP real detrás del proxy, imagen de producción con gunicorn, `README.md` y la guía del panel.

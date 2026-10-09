# Tareas — specs-004

> Pasos pequeños y verificables. Se hace **una tarea a la vez** y se marca `[x]` solo cuando se cumple su **verificación**.
> Cada tarea indica qué requisito cubre de `specs/specs-004/requirements.md`.

**Leyenda:** `[ ]` pendiente · `[x]` hecha · `[~]` en progreso · `[!]` bloqueada (anota el motivo)

Las tareas llevan el prefijo `S4-`. **Este paquete se entrega por bloques** (P-41): cada bloque incluye su backend y su frontend, se sube como commit local y termina en una pausa ✋ para que el desarrollador lo pruebe antes de seguir.

---

## Fase A — Especificación

- [x] **S4-A1** Plan de los 10 cambios, con las preguntas al desarrollador (P-31 a P-34).
- [x] **S4-A2** Crear `specs/specs-004/requirements.md`, `design.md` y `tasks.md`.
- [x] **S4-A3** Actualizar `AGENTS.md`: specs-004 es el trabajo en curso y el despliegue sigue siendo la última fase.
- [ ] **S4-A4** ✋ **Aprobación** de specs-004 y de las decisiones P-35 a P-40.

---

## Bloque 1 — Formulario

- [x] **S4-B1** "Ubicación del espacio" con el mismo ancho que "Tipo de remodelación". *(RF-40.1, CA-40.1)*
- [x] **S4-B2** "Tengo fotos del espacio" arriba del mensaje, en el sitio y en la tabla del panel (migración de datos `site_content.0013`). *(RF-40.2, RF-40.3, CA-40.2)*
- [ ] **S4-B3** ✋ **Prueba del bloque 1:** el desarrollador revisa el formulario.

---

## Bloque 2 — Servicios

- [ ] **S4-C1** `Service.image` e `image_alt`; "Servicios (encabezado)" pasa a "Servicios". Migración `site_content.0014`. *(RF-36)*
- [ ] **S4-C2** Imagen en la tabla de servicios del panel y en `/api/site/`, con sus tests (API, panel, archivo falso, Viewer). *(RF-36, CA-36.1 a CA-36.3)*
- [ ] **S4-C3** `styles/overlay.css` y el token `--motion-overlay`: capa compartida con entrada suave, barra fina y degradado. *(RF-37.2, RF-38)*
- [ ] **S4-C4** `ServiceCard` y sección Servicios con fondo oscuro y cuadrícula de portadas. *(RF-35, CA-35.1, CA-35.2)*
- [ ] **S4-C5** Capa con la descripción y "Cotizar": con cursor, con teclado y con "reducir movimiento". *(RF-37, CA-37.1 a CA-37.3)*
- [ ] **S4-C6** En táctil, la descripción y "Cotizar" entran al aparecer la tarjeta. *(RF-41.2, CA-41.2)*
- [ ] **S4-C7** ✋ **Prueba del bloque 2:** el desarrollador carga una imagen en un servicio y revisa la sección en computadora y celular.

---

## Bloque 3 — Proyectos

- [ ] **S4-D1** Sección Proyectos del inicio con título y botón grande; `Button` tamaño "large"; se borran `ProjectCategories` y `CategoryCard`. *(RF-34, CA-34.1 a CA-34.3)*
- [ ] **S4-D2** Texto del botón "Ver proyectos" (migración de datos `site_content.0015`, con su test) y panel sin "usar como portada de su categoría". *(RF-34.3, P-37, P-38)*
- [ ] **S4-D3** Tarjetas de proyecto con la capa compartida (barra fina y degradado). *(RF-38, CA-38.1, CA-38.2)*
- [ ] **S4-D4** Capa con la descripción sobre la portada del detalle. *(RF-39, CA-39.1, CA-39.2)*
- [ ] **S4-D5** En táctil, el texto de las tarjetas de proyecto entra suave. *(RF-41.3)*
- [ ] **S4-D6** Revisión responsive (360, 768, 1280 y 1920 px) y de accesibilidad de todo el paquete. *(RNF-16, RNF-17)*
- [ ] **S4-D7** ✋ **Prueba del bloque 3:** `manage.py test`, `npm test`, `npm run lint` y `npm run build` pasan; el desarrollador revisa el sitio en computadora y celular.

---

## Fase E — Cierre

- [ ] **S4-E1** Actualizar `docs/problemas-frecuentes.md` si apareció algún error nuevo.
- [ ] **S4-E2** Anotar en `specs/` y en los paquetes anteriores qué apartados quedaron sustituidos por specs-004.
- [ ] **S4-E3** ✋ Aprobación final.

---

## Después de specs-004: despliegue

> ⚠️ **Sigue pendiente y no se ha empezado.** Las tareas están en `specs/tasks.md`, **Fase 5 (T-5.1 a T-5.9)**.

| Qué | Depende de |
|---|---|
| T-5.1 Dominio y DNS en Cloudflare | Que el cliente compre el dominio |
| T-5.2 Bucket R2 y almacenamiento de archivos | Cuenta de Cloudflare. **El código de R2 todavía no está escrito** (`specs/design.md` §2.11). También guardará las fuentes y las imágenes de los servicios |
| T-5.3 y T-5.4 Backend y base de datos en Railway | Cuenta de Railway. Falta la imagen de producción con gunicorn |
| T-5.5 y T-5.6 Frontend en Cloudflare Pages y dominios | Lo anterior |
| T-5.7 Lista de comprobación de seguridad | Incluye leer la IP real detrás del proxy y que no quede ningún `[TEXTO PENDIENTE]` legal |
| T-5.8 Lighthouse | Sitio publicado |
| T-5.9 Guía de uso del panel para el cliente | — |

Lo que se puede adelantar **sin dominio ni cuentas**: almacenamiento en R2 por variables de entorno, lectura de la IP real detrás del proxy, imagen de producción con gunicorn, `README.md` y la guía del panel.

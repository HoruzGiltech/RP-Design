# Tareas — specs-001

> Pasos pequeños y verificables. Se hace **una tarea a la vez** y se marca `[x]` solo cuando se cumple su **verificación**.
> Cada tarea indica qué requisito cubre de `specs/specs-001/requirements.md`.

**Leyenda:** `[ ]` pendiente · `[x]` hecha · `[~]` en progreso · `[!]` bloqueada (anota el motivo)

Las tareas llevan el prefijo `S1-` para no confundirlas con las de `specs/tasks.md`.

---

## Fase A — Especificación

- [x] **S1-A1** Crear `specs/specs-001/requirements.md`, `design.md` y `tasks.md`.
- [x] **S1-A2** Actualizar `AGENTS.md` para que specs-001 sea el trabajo en curso, antes del despliegue.
- [x] **S1-A3** ✋ **Aprobación** de specs-001 y de las decisiones P-1 a P-7 (`requirements.md` §4). (Aprobado el 2026-10-06.)
- [x] **S1-A4** Mover el paquete a `specs/specs-001/`: todas las specs van dentro de `specs/`.

---

## Fase B — Backend

### B1. Dirección web automática
- [x] **S1-B1** `projects/services.py`: `build_base_slug` y `make_unique_slug`. *(RF-10.2, RF-10.3)*
  - Verificación: tests: "Remodelación de cocina" → `remodelacion-de-cocina`; "Casa" → `proyecto-casa`; repetido → `-2`; sin letras → `proyecto`.
- [x] **S1-B2** `Project.slug` no editable y generado solo al crear; sale del formulario del panel y se muestra en solo lectura. *(RF-10.1, RF-10.4, CA-10.1, CA-10.3)*
  - Verificación: tests de que editar el título no cambia la dirección y de que el formulario no tiene el campo.

### B2. Categorías
- [x] **S1-B3** Modelo `ProjectCategory` y campos nuevos en `Project` (`category_fk`, `show_in_hero`, `hero_order`, `is_category_cover`). Migración `0002`. *(RF-09.1, RF-08.1)*
- [x] **S1-B4** Migración de datos `0003`: crea las 3 categorías, asocia los proyectos por el texto antiguo y copia destacados → hero. *(RF-09.2, CA-09.1, CA-09.6)*
  - Verificación: test de migración: "Fachada · Residencial" → Residencial; texto sin coincidencia → vacío.
- [x] **S1-B5** Migración `0004`: elimina `category` de texto, `is_featured` y `featured_order`; renombra `category_fk` → `category`. *(RF-08.10)*
  - Verificación: `makemigrations --check` sin cambios pendientes; los proyectos de prueba conservan sus datos.
- [x] **S1-B6** Reglas del modelo: máximo 6 en el hero y una sola portada por categoría. *(RF-08.11, RF-09.8)*
  - Verificación: tests: el 7.º falla con mensaje en español; marcar otra portada desmarca la anterior.
- [x] **S1-B7** Panel: `ProjectCategory` ordenable y protegida contra borrado con proyectos; `Project` con categoría obligatoria, bloque "Publicación" nuevo, columnas y filtros. *(RF-09.1, RF-09.11)*
  - Verificación: tests del panel y prueba en navegador con Playwright.
- [x] **S1-B8** Migración `core.0003`: permisos de `ProjectCategory` para Admin y Viewer.
  - Verificación: pasa el test de roles que avisa de permisos olvidados.

### B3. API
- [x] **S1-B9** `GET /api/projects/`: filtros `?hero=true` y `?category=<slug>`; `category` como objeto; `cover_image` en la tarjeta. Se quita `?featured=true`. *(RF-08.2, RF-09.4, CA-08.3, CA-09.4)*
  - Verificación: tests: borradores fuera, orden del hero, máximo 6, slug inexistente devuelve todos.
- [x] **S1-B10** `GET /api/project-categories/`. *(RF-09.3, RF-09.7, RF-09.9, CA-09.5)*
  - Verificación: tests: oculta las vacías, cuenta solo publicados, usa la portada marcada o la del primero.

### B4. WhatsApp y Portada
- [x] **S1-B11** `site_content/services.py`: `format_whatsapp_number`. Se elimina `whatsapp_display` del modelo y se calcula en la API. *(RF-11)*
  - Verificación: tests: `584127305964` → `+58 412 730 5964`; otro país → `+` y dígitos.
- [x] **S1-B12** `SiteSettings`: `whatsapp_greeting` y `show_whatsapp_button`, en el panel y en `/api/site/`. *(RF-12.2, RF-12.3)*
- [x] **S1-B13** Migración de datos: título de la Portada vacío y botón "Agenda una reunión", solo si siguen con el texto original. `HeroSection.title` admite vacío. *(RF-08.6, RF-08.8, CA-08.9)*
  - Verificación: test de que un título cambiado por el cliente no se toca.

- [x] **S1-B14** ✋ **Revisión de fin de fase:** `manage.py test` completo y demo del panel (categorías, casillas nuevas, botón flotante). (Aprobada el 2026-10-06.)

---

## Fase C — Frontend

- [x] **S1-C1** `api/endpoints.js` y `utils/whatsapp.js` (`buildWhatsAppLink`) con sus tests en Vitest. `ContactInfo` pasa a usar la utilidad. *(RF-11.1, CA-11.1)*
  - Verificación: en Contacto se lee "WhatsApp: +58 412 730 5964".
- [x] **S1-C2** `ProjectCard` y `ProjectDetailPage` con `category` como objeto. *(RF-09.10)*
- [x] **S1-C3** `hooks/useSlideshow.js`: portada activa, intervalo, pausa por pestaña oculta, por cursor y por foco. *(RF-08.3, RF-08.5)*
- [x] **S1-C4** Hero nuevo: distribución a todo el ancho, capa oscura, texto, portadas, nombre del proyecto con enlace, controles e indicadores. Tokens nuevos. *(RF-08.2 a RF-08.7)*
  - Verificación con Playwright: 3 portadas rotan; 1 queda fija y sin controles.
- [x] **S1-C5** Animación del hero en `motion.css` (fundido y zoom lento) y comportamiento con movimiento reducido. Título principal oculto cuando el título está vacío. *(RF-08.3, CA-08.5 a CA-08.8)*
- [x] **S1-C6** Respaldo del hero con la imagen o el video de la Portada cuando no hay proyectos marcados. *(RF-08.9, CA-08.1)*
- [x] **S1-C7** `ProjectCategories` y `CategoryCard` en el inicio; se borra `FeaturedProjects`. *(RF-09.3, RF-09.6, RF-09.7, CA-09.2)*
- [x] **S1-C8** `/proyectos` con `?categoria=` y `CategoryFilter`; título de la página y de la pestaña según la categoría. *(RF-09.4, RF-09.5, CA-09.3, CA-09.4)*
  - Verificación con Playwright: inicio → categoría → filtro → botón atrás.
- [x] **S1-C9** `WhatsAppButton` en `Layout`, con el ajuste de espacios para que no tape nada. *(RF-12, CA-12.1 a CA-12.4)*
  - Verificación con Playwright a 360 px: no tapa el envío del formulario ni el pie; queda por debajo del visor.
- [x] **S1-C10** Revisión responsive (360, 768, 1280 y 1920 px) y de accesibilidad de lo nuevo: contraste del texto sobre las portadas, teclado en los controles del hero, nombres accesibles. *(RNF-09, RNF-10)*

- [x] **S1-C10b** Título de la sección de categorías: "Mis Proyectos" (migración `site_content.0008`). *(P-6)*

- [x] **S1-C10c** Subir la sección Proyectos por encima de Servicios en `HomePage.jsx`. *(P-8, CA-13.1, CA-13.2)*
  - Verificación con Playwright a 360 y 1280 px: orden correcto y el enlace "Proyectos" del menú llega a la sección.
- [x] **S1-C10d** Franja: "Renders 3D" → "Corporativo" (migración `site_content.0009`) con su test. *(P-9, CA-13.3, CA-13.4)*

- [x] **S1-C11** ✋ **Revisión de fin de fase:** `npm test`, `npm run lint` y `npm run build` pasan; demo del sitio con datos cargados desde el panel y prueba en un celular real. (Dada por cerrada el 2026-10-07: el desarrollador revisó el sitio y pasó a specs-002.)

---

## Fase D — Cierre

- [x] **S1-D1** Actualizar `docs/problemas-frecuentes.md` si apareció algún error nuevo.
- [x] **S1-D2** Anotar en `specs/requirements.md` y `specs/design.md` qué apartados quedaron sustituidos por specs-001, para que nadie programe sobre la versión vieja.
- [x] **S1-D3** ✋ Aprobación final. Después sigue la Fase 5 (despliegue) de `specs/tasks.md`. (Dada por cerrada el 2026-10-07: el desarrollador revisó el sitio y pasó a specs-002.)

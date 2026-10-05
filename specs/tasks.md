# Tareas — Web RP Design

> Pasos pequeños y verificables. Se hace **una tarea a la vez** y se marca `[x]` solo cuando se cumple su **verificación**.
> Cada tarea indica qué requisito cubre (`RF-xx` / `CA-xx`).

**Leyenda:** `[ ]` pendiente · `[x]` hecha · `[~]` en progreso · `[!]` bloqueada (anota el motivo)

---

## Fase 1 — Especificación

- [x] **T-1.1** Crear `specs/requirements.md`, `specs/design.md` y `specs/tasks.md`.
- [x] **T-1.2** Guardar la maqueta en `docs/`: `maqueta-original.html` (el archivo del diseñador, empaquetado) y `maqueta-legible.html` (el HTML extraído, para leerlo y compararlo).
- [x] **T-1.3** Completar el inventario de secciones (§3 de requirements) y los modelos de `site_content` (§2.3 de design) según la maqueta.
- [x] **T-1.4** Extraer los design tokens de la maqueta a `design.md` §3.0.
- [ ] **T-1.4b** Confirmar con el cliente la ortografía del correo (`rpdesings05@gmail.com`) y si quiere secciones Nosotros o Testimonios (hoy están fuera de alcance). No bloquea la Fase 2.
- [x] **T-1.5** ✋ **Aprobación del cliente/desarrollador** de las tres specs. *No se programa nada antes de esto.* (Aprobadas el 2026-10-05.)
- [x] **T-1.6** Alinear `AGENTS.md` y `CLAUDE.md` con las specs (apps `core` y `site_content`, rutas de la maqueta, Nosotros/Testimonios como pregunta abierta) y documentar el uso de las skills en `design.md` §3.5.

- [x] **T-1.7** Agregar RF-06 Animaciones (referencia: sparquitectosve.com) a `requirements.md`, `design.md` §3.0 y §3.6, y a `AGENTS.md`.
- [x] **T-1.8** ✋ **Aprobación** de RF-06 y del video opcional de la Portada. (Aprobado el 2026-10-05.)

---

## Fase 2 — Backend

### 2A. Base del proyecto
- [x] **T-2.1** Crear la estructura de carpetas, `.gitignore` (incluye `.env`, `media/`, `node_modules/`, `__pycache__/`, `*.sqlite3`) y `.env.example`. Las carpetas `backend/` y `frontend/` aparecen en T-2.2 y T-3.1, porque git no guarda carpetas vacías.
  - Verificación: `git status` no muestra `.env`.
- [x] **T-2.2** `docker-compose.yml` con `db` y `backend`; proyecto Django `config/` que lee `.env` con `django-environ`.
  - Verificación: `docker compose up` levanta el servicio y `http://localhost:8000/<ADMIN_URL>` muestra el login.
- [x] **T-2.3** Configurar el idioma `es`, la zona horaria `America/Caracas`, DRF, CORS, whitenoise y `ADMIN_URL` desde `.env`.
  - Verificación: el login del panel aparece en español y `/admin/` da 404.

### 2B. App `core`
- [x] **T-2.4** Clases base `TimeStampedModel`, `OrderedModel`, `VisibleModel` y `SingletonModel`. *(RF-05.2)*
  - Verificación: test de que `SingletonModel` siempre tiene `pk=1` y `delete()` no lo borra.
- [ ] **T-2.5** Validadores de archivos: extensión, tamaño y contenido real. *(RF-02.3, RF-02.4, CA-02.1, CA-02.2)*
  - Verificación: tests con un `.exe` renombrado y con un archivo que supera el límite.
- [ ] **T-2.6** Procesamiento de imágenes: EXIF, 1920 px, miniatura de 600 px y renombrado con uuid. *(RF-02.5)*
  - Verificación: test de que, tras subir una imagen de 4000 px, la guardada mide ≤ 1920 px y existe la miniatura.

### 2C. App `projects`
- [ ] **T-2.7** Modelos `Project` y `ProjectMedia` y su migración.
- [ ] **T-2.8** Validar el máximo de 3 destacados en `clean()`. *(CA-01.1)*
  - Verificación: test de que el 4.º destacado lanza `ValidationError` con un mensaje en español.
- [ ] **T-2.9** Admin de proyectos: ordenable, inline de media ordenable, vista previa y filtros. *(RF-04.2, RF-04.3)*
  - Verificación manual: crear un proyecto con 3 imágenes y 1 video, reordenarlos arrastrando y comprobar que el orden se guarda.

### 2D. App `quotes`
- [ ] **T-2.10** Modelos `RemodelArea` y `Quote`, más la migración de datos con las 6 áreas iniciales. *(RF-03.2)*
- [ ] **T-2.11** `services.py`: `calculate_estimate`, `format_usd`, `build_whatsapp_message` y `build_whatsapp_link`. *(RF-03.4 a RF-03.6, CA-03.1)*
  - Verificación: tests unitarios: `12.5 × 100 = USD 1.250,00`; área sin precio → "A cotizar"; el mensaje incluye todos los campos; se omite la línea del mensaje cuando está vacío.
- [ ] **T-2.12** Admin de áreas (precios editables en la lista) y de cotizaciones (solo lectura salvo el estado, con filtros, búsqueda y enlace a WhatsApp). *(RF-04.4, RF-04.7)*

### 2E. App `site_content`
- [ ] **T-2.13** Modelos `SiteSettings` (incluye `accent_color`) y las secciones únicas `HeroSection` (con `video` opcional, RF-06.5), `ServicesSection`, `ProjectsSection`, `ProcessSection`, `ContactSection`, `FooterSection` y `SeoSettings`. *(RF-05, RF-04.5)*
- [ ] **T-2.14** Modelos de lista `Specialty`, `Service` y `ProcessStep`.
- [ ] **T-2.14b** Migración de datos con **todos los textos y datos de contacto de la maqueta** (design §2.3). *(CA-05.3, D-14)*
  - Verificación: con una BD nueva, `GET /api/site/` devuelve los mismos textos que `docs/maqueta-legible.html`.
- [ ] **T-2.15** Admin: las secciones únicas sin "Agregar" ni "Eliminar"; las listas ordenables con `is_visible`. *(RF-05.2 a RF-05.4)*
  - Verificación manual: no se puede crear un segundo Hero.

### 2F. Roles
- [ ] **T-2.16** Migración de datos que crea los grupos **Admin** y **Viewer** con sus permisos. *(RF-04.8, CA-04.3)*
  - Verificación: con una BD nueva, después de `migrate`, ambos grupos existen con los permisos esperados.
- [ ] **T-2.17** Tests de permisos: el Viewer recibe 403 al crear, editar o borrar, y el Admin puede todo. *(CA-04.1, CA-04.2, CA-04.4)*

### 2G. API
- [ ] **T-2.18** Serializers y `GET /api/site/`. *(RF-05.1)*
  - Verificación: la respuesta incluye todas las secciones; las ocultas llegan con `is_visible: false`.
- [ ] **T-2.19** `GET /api/projects/` (con `?featured=true`) y `GET /api/projects/<slug>/`. *(RF-01.1 a RF-01.5)*
  - Verificación: tests de que un borrador da 404 y de que el orden de destacados y de media es el correcto.
- [ ] **T-2.20** `GET /api/quote-areas/`.
- [ ] **T-2.21** `POST /api/quotes/`: validación, recálculo, guardado del mensaje y respuesta con `whatsapp_url`. *(RF-03.8, CA-03.2, CA-03.4)*
  - Verificación: test que envía un `estimated_price` falso y comprueba que se ignora.
- [ ] **T-2.22** Honeypot con respuesta 201 falsa sin guardar nada. *(D-10)*
- [ ] **T-2.23** Throttles `public` y `quotes`. *(RNF-05)*
  - Verificación: test de que el 6.º POST en una hora devuelve 429.

### 2H. Seguridad del panel
- [ ] **T-2.24** `django-axes` (5 intentos → 30 min) y validadores de contraseña.
  - Verificación manual: 5 logins fallidos bloquean el acceso.
- [ ] **T-2.25** Configuración de producción en `settings` (DEBUG, cookies seguras, HSTS, SSL), activada por `.env`.
  - Verificación: `python manage.py check --deploy` sin advertencias críticas con `DEBUG=False`.

- [ ] **T-2.26** ✋ **Revisión de fin de fase:** `manage.py test` pasa completo y se hace una demo del panel.

---

## Fase 3 — Frontend

- [ ] **T-3.1** Proyecto Vite + React + React Router, servicio `frontend` en Docker Compose, ESLint y `frontend/.env.example`.
  - Verificación: `npm run dev` muestra la página y `npm run lint` pasa.
- [ ] **T-3.2** `styles/tokens.css` (todos los tokens de design §3.0, incluidos los de movimiento) y `global.css`, más las fuentes con `@fontsource`. *(RNF-02, D-16)*
- [ ] **T-3.3** `api/client.js`, `api/endpoints.js`, `useFetch` y `SiteContext`.
  - Verificación: en consola se ve el JSON de `/api/site/`.
- [ ] **T-3.4** Componentes `ui/`: Button (con `scale(0.97)` al pulsar), Spinner, ErrorMessage y Section.
- [ ] **T-3.4b** `hooks/useReveal.js`, `ui/Reveal` y `styles/motion.css` con la regla de `prefers-reduced-motion`. *(RF-06.1, RF-06.8, RF-06.9, CA-06.3)*
  - Verificación: un elemento de prueba aparece una sola vez al entrar en pantalla; con "reducir movimiento" se ve desde el inicio.
- [ ] **T-3.5** Layout: Header (logo y menú responsive con hamburguesa) y Footer. *(S1, S8)*
- [ ] **T-3.6** Hero, con entrada del título y los botones, video opcional y zoom ligado al scroll. *(S2, RF-06.1, RF-06.2, RF-06.5, RF-06.6, CA-06.5)*
- [ ] **T-3.7** FeaturedProjects (fondo oscuro, enlace a Instagram y botón "Ver todos") y ProjectCard (capa "Ver proyecto" al pasar el cursor y entrada escalonada); la sección se oculta si hay 0 destacados. *(S5, RF-01.1, CA-01.2, RF-06.3, RF-06.7)*
- [ ] **T-3.8** SpecialtiesStrip (cinta con `ui/Marquee`), Services (entrada izquierda / abajo / derecha) (números 01, 02… calculados) y Process (letras A, B… calculadas y video); se ocultan si están vacíos o desactivados. *(S3, S4, S6, CA-05.2, D-13, RF-06.3, RF-06.4, CA-06.4)*
- [ ] **T-3.8b** `MediaPlaceholder` en sus variantes clara y oscura, y color de acento aplicado desde `settings.accent_color`. *(CA-05.3, CA-05.4)*
- [ ] **T-3.8c** Contact: columna de datos (WhatsApp, correo, Instagram y ciudad desde SiteSettings) y espacio para la calculadora. *(S7)*
- [ ] **T-3.9** `ProjectsPage` con ProjectGrid y miniaturas con `loading="lazy"`. *(RF-01.2, CA-02.3)*
- [ ] **T-3.10** `ProjectDetailPage` con MediaGallery y Lightbox (teclado: Esc y flechas). *(RF-01.3, RF-02.6)*
- [ ] **T-3.11** `NotFoundPage` y manejo de slugs inexistentes. *(CA-01.5)*
- [ ] **T-3.12** `useDocumentTitle` en cada página, con los datos de `SeoSettings`.
- [ ] **T-3.13** Revisión responsive: 360, 768, 1280 y 1920 px. *(RNF-01)*
  - Verificación: capturas en cada ancho comparadas con `docs/maqueta-legible.html`.
- [ ] **T-3.13b** Revisión de animaciones con Playwright: recorrido normal y con `prefers-reduced-motion` emulado. *(CA-06.1, CA-06.2, CA-06.6)*

- [ ] **T-3.14** ✋ **Revisión de fin de fase:** `npm run lint` y `npm run build` pasan; demo navegando todo el sitio con datos reales cargados desde el panel.

---

## Fase 4 — Calculadora y WhatsApp

- [ ] **T-4.1** `utils/currency.js` y `utils/estimate.js`, con tests en Vitest (mismos casos que el backend). *(RF-03.4, RF-03.6)*
- [ ] **T-4.2** Formulario `QuoteCalculator`: campos, validación y campo "Especifique" para "Otro". *(RF-03.1, RF-03.2, CA-03.6)*
- [ ] **T-4.3** `EstimateDisplay`: estimado en vivo, "A cotizar" y `price_note`. *(RF-03.5, RF-03.7)*
- [ ] **T-4.4** Envío: POST, botón deshabilitado mientras se envía, `location.assign(whatsapp_url)` y pantalla de éxito con "Abrir WhatsApp". *(RF-03.9, CA-03.5)*
- [ ] **T-4.5** Manejo de errores 400 (por campo) y 429 (mensaje amable).
- [ ] **T-4.6** Honeypot en el formulario.
- [ ] **T-4.7** Prueba completa de punta a punta:
  1. Configurar en el panel el número de WhatsApp y el precio de Cocina a 100 USD.
  2. En el sitio: Cocina, 12,5 m² → se muestra "USD 1.250,00".
  3. Enviar → se abre WhatsApp con el mensaje completo.
  4. En el panel aparece la cotización con estado `nuevo` y el mensaje guardado.
  5. Cambiar el precio a 120 → al recargar, el sitio muestra "USD 1.500,00" y la cotización anterior sigue en 1.250,00.
  - Probar en un celular real (Android y iOS si es posible).

- [ ] **T-4.8** ✋ **Revisión de fin de fase** y revisión de accesibilidad: formulario con teclado, contraste y `alt`. *(RNF-04)*

---

## Fase 5 — Despliegue *(cuando el cliente compre el dominio)*

- [ ] **T-5.1** Comprar el dominio y agregarlo a Cloudflare (DNS).
- [ ] **T-5.2** Crear el bucket en Cloudflare R2, el token de acceso con permisos mínimos y el dominio `media.<dominio>`.
- [ ] **T-5.3** Railway: crear el servicio del backend y Postgres, configurar las variables de entorno de producción y usar `gunicorn`.
- [ ] **T-5.4** Ejecutar `migrate` y `collectstatic`, y crear el superusuario del desarrollador y el usuario Admin del cliente (`is_staff` + grupo Admin, **no** superusuario).
- [ ] **T-5.5** Cloudflare Pages: conectar el repositorio, `npm run build`, `VITE_API_URL` de producción y la regla de rutas SPA (`_redirects`: `/* /index.html 200`).
- [ ] **T-5.6** Dominios: `<dominio>` → Pages y `api.<dominio>` → Railway; actualizar `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS` y `FRONTEND_URL`.
- [ ] **T-5.7** Checklist de seguridad en producción:
  - [ ] `check --deploy` limpio
  - [ ] `.env` fuera del repositorio (revisar también el historial de git)
  - [ ] HTTPS en los tres dominios
  - [ ] El rate limit responde 429
  - [ ] La URL del panel no es `/admin/`
  - [ ] Respaldos de Postgres activos
- [ ] **T-5.8** Lighthouse en móvil: Performance ≥ 85, Accesibilidad ≥ 90. *(RNF-03)*
- [ ] **T-5.9** Entrega al cliente: guía corta de uso del panel (cómo subir un proyecto, cambiar precios y ver cotizaciones).

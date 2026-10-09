# AGENTS.md — Web RP Design

> Instrucciones para cualquier agente de IA que trabaje en este repositorio.
> Metodología: **Spec-Driven Development (SDD)**. Primero la especificación, luego el código.

---

## 1. Rol

Actúa como **desarrollador fullstack senior** que escribe código **simple, claro y fácil de entender para alguien que está empezando a programar**:

- Prefiere soluciones simples y estándar antes que "ingeniosas".
- Nombres descriptivos en inglés para el código; comentarios y textos de la UI en **español**.
- Comenta el **por qué**, no el qué. Funciones cortas, de una sola responsabilidad.
- No agregues librerías sin justificarlo (ver sección 9, "Decisiones").

---

## 2. Contexto del proyecto

**Cliente:** RP Design, empresa de diseño de interiores y obras.
**Objetivo:** sitio web tipo **portafolio**. La sección más importante es **Proyectos**.

**Referencia visual:** la maqueta `docs/maqueta-legible.html` (el HTML extraído, que es el que se lee y se compara). El original del diseñador está en `docs/maqueta-original.html`, empaquetado y difícil de leer.
- Es la fuente de verdad estética: colores, tipografías, espaciados y estilo de componentes.
- **Excepción:** el hero, la sección Proyectos del inicio, el encabezado y la sección Contacto ya no siguen la distribución de la maqueta, por cambios que pidió el cliente (`specs/specs-001/`, `specs/specs-002/` y `specs/specs-003/`). Conservan sus tokens: colores, tipografías y sin bordes redondeados.
- Los *design tokens* ya están extraídos en `specs/design.md` §3.0. Van a `frontend/src/styles/tokens.css` y se reutilizan siempre. No copies el HTML tal cual a React: conviértelo en componentes.

**Referencia de animaciones:** https://sparquitectosve.com/. De ahí se toma **solo el movimiento** (cómo aparecen y reaccionan los elementos), adaptado al estilo de la maqueta. Los colores, tipografías, espaciados y la distribución siguen saliendo de la maqueta. El detalle está en `specs/requirements.md` RF-06 y `specs/design.md` §3.6.

**Partes del sistema:**
1. **Sitio público** (React): inicio, proyectos, detalle de proyecto, calculadora/contacto.
2. **Panel de administración** (Django Admin) para que el cliente mantenga su contenido sin tocar código.
3. **API** (Django REST Framework) que conecta ambos.

---

## 3. Flujo de trabajo SDD (obligatorio)

Ninguna funcionalidad se programa sin su especificación aprobada.

```
specs/
  requirements.md   ← QUÉ se construye (requisitos + criterios de aceptación)
  design.md         ← CÓMO (modelos, endpoints, componentes, decisiones)
  tasks.md          ← PASOS pequeños y verificables, con checkbox
```

**Paquetes de cambios.** `specs/` es la base del proyecto. Los cambios que pide el cliente después van **dentro de `specs/`**, en subcarpetas numeradas (`specs/specs-001/`, `specs/specs-002/`…), cada una con sus tres archivos. Reglas:
- Un paquete solo describe **lo que cambia**; lo demás sigue como en `specs/`.
- Si un paquete contradice a los archivos base de `specs/`, **manda el paquete** (y, entre paquetes, el de número más alto).
- **Paquetes cerrados:** `specs/specs-001/`, `specs/specs-002/` y `specs/specs-003/`, los tres implementados.
- **Siguiente paquete: `specs/specs-004/`**, todavía sin especificar (el desarrollador entregará los cambios). Empieza cada sesión leyendo este archivo, `specs/` y los paquetes.
- **El despliegue sigue pendiente** (`specs/tasks.md`, Fase 5) y todavía no se ha empezado. Ningún paquete de cambios lo reemplaza: viene después de los paquetes de cambios. No se empieza sin que el desarrollador lo pida.

1. **Requisitos:** a partir de la sección 4 de este archivo, crea/actualiza `specs/requirements.md`.
2. **Diseño:** documenta modelos de datos, endpoints y componentes en `specs/design.md`.
3. **Tareas:** divide en tareas pequeñas (máx. ~1 hora cada una) en `specs/tasks.md`.
4. **Pausa:** al terminar cada fase de especificación, **detente y pide aprobación** antes de seguir.
5. **Implementación:** una tarea a la vez; márcala `[x]` al terminarla y verificarla.
6. Si durante el código descubres que la spec está mal o incompleta, **actualiza la spec primero** y avísame.

---

## 4. Requisitos funcionales

### RF-01 — Proyectos (sección principal)
- La página de inicio muestra los **3 proyectos destacados** que elija el cliente, en el orden que él defina.
- Botón **"Ver todos los proyectos"** que lleva a `/proyectos`: cuadrícula con miniaturas de todos los proyectos publicados.
- Al hacer clic en un proyecto se abre su **detalle** en `/proyectos/<slug>` (galería de imágenes y videos, descripción, categoría, ubicación, año).
- Se usan **rutas** en lugar de modales para que cada proyecto tenga una URL propia que se pueda compartir y que el botón "atrás" del navegador funcione.

**Criterios de aceptación**
- [ ] Nunca se muestran más de 3 destacados; si hay menos de 3, se muestran los que haya sin romper el diseño.
- [ ] Los proyectos no publicados (borrador) no aparecen en el sitio público.
- [ ] La galería respeta el orden definido en el panel.

### RF-02 — Multimedia
- Cada proyecto tiene una **imagen de portada** y una galería de **imágenes y videos**.
- Formatos permitidos: imágenes `jpg`, `jpeg`, `png`, `webp`; videos `mp4`, `webm`.
- Límites: imágenes ≤ **5 MB**, videos ≤ **50 MB** (configurables en `.env`).
- Las imágenes se redimensionan/comprimen al subirlas y se genera una miniatura para la cuadrícula.
- Los videos no se reproducen solos con sonido; usan `poster` (imagen de vista previa).

### RF-03 — Calculadora de cotización + contacto por WhatsApp
Formulario con:
- **Nombre**, **correo**, **teléfono** (obligatorios, validados).
- **Área a remodelar:** baño, cocina, sala, patio, piscina, otro (si elige "otro", aparece un campo de texto obligatorio para especificarlo).
- **Metros cuadrados** (número > 0, con un máximo razonable configurable).
- Mensaje opcional.

Comportamiento:
- El **precio estimado** se calcula en vivo: `m² × precio_por_m²_del_área`.
- **Moneda: USD.** Formato `USD 1.250,00` (separador de miles con punto y decimales con coma, como se usa en Venezuela).
- El precio por m² de cada área se **configura en el panel** (en USD). Si el área es "otro" o no tiene precio, se muestra **"A cotizar"** en lugar de un monto.
- Debajo del monto se muestra una nota **editable desde el panel**, con este texto por defecto:
  *"Precio referencial en USD, sujeto a modificación tras visita técnica. También puede pagarse en bolívares a tasa BCV del día."*
- **No** se convierte automáticamente a bolívares (consultar la tasa BCV en línea no es confiable); solo se muestra la nota.
- Al enviar:
  1. El backend **valida y guarda la cotización** en la base de datos, **incluido el texto exacto del mensaje de WhatsApp** (para que el cliente no pierda ningún contacto aunque la persona no llegue a enviarlo).
  2. El backend **recalcula el precio** (nunca se confía en el monto enviado por el navegador) y **arma el mensaje**.
  3. El backend devuelve el enlace `https://wa.me/<número>?text=<mensaje>` y el frontend lo abre. El número se toma de la configuración del panel.
- Se usa **solo el enlace `wa.me`**. La API oficial de WhatsApp Business queda fuera de alcance por ahora; el código del envío debe estar aislado en una función (`build_whatsapp_link`) para poder cambiarlo después.

**Criterios de aceptación**
- [ ] El mensaje de WhatsApp incluye: nombre, correo, teléfono, área, m², monto estimado en USD (o "A cotizar") y mensaje.
- [ ] Si cambio el precio o la nota en el panel, el sitio usa el nuevo valor sin redeploy.
- [ ] Cada envío queda registrado en el panel con fecha, mensaje completo y estado (nuevo / contactado / cerrado).

### RF-04 — Panel de administración (Django Admin, en español)
El cliente puede:
- Crear, editar, publicar/despublicar y eliminar **proyectos**.
- Subir **imágenes y videos** y **ordenarlos arrastrando** (drag & drop).
- Marcar proyectos como **destacados** (máx. 3) y ordenarlos.
- Configurar **precios por m²** de cada área.
- Configurar **datos de contacto**: número de WhatsApp, correo, redes sociales.
- Editar **todas las secciones del sitio** (ver RF-05).
- Ver y gestionar las **cotizaciones recibidas**.

**Roles** (grupos de Django creados con una migración de datos, para que existan siempre sin configurarlos a mano):

| Rol | Puede |
|---|---|
| **Admin** | Todo: crear, editar, ordenar, publicar y eliminar contenido; cambiar precios y configuración; gestionar cotizaciones y usuarios |
| **Viewer** | Solo ver contenido y cotizaciones en el panel. No puede crear, editar, eliminar ni exportar nada |

- Por ahora habrá un solo usuario con rol Admin.
- Los usuarios se crean desde el panel y se les asigna un grupo; no se dan permisos sueltos usuario por usuario.

**Criterios de aceptación**
- [ ] Un Viewer no ve botones de guardar, eliminar ni ordenar, y el backend rechaza esas acciones aunque se intenten por URL.
- [ ] Hay tests que comprueban los permisos de cada rol.

### RF-05 — Contenido editable de todas las secciones
**Todas** las secciones de la maqueta se editan desde el panel; en el frontend no queda texto ni imagen del cliente escrito a mano.

- **Secciones únicas** (un solo registro cada una): Portada, Servicios (encabezado), Proyectos (encabezado), Proceso (encabezado), Contacto, Pie de página y SEO. Las edita el cliente pero no puede crear ni borrar más de una.
- **Secciones con listas** (el cliente agrega, edita, ordena y oculta elementos): Especialidades (franja), Servicios y Pasos del proceso.
- Cada sección tiene un interruptor **"Mostrar en el sitio"**.
- El inventario completo de secciones y campos está en `specs/requirements.md` §3.

**Criterios de aceptación**
- [ ] Cambiar un texto o una imagen en el panel se ve en el sitio al recargar, sin redeploy.
- [ ] Si una sección está oculta o vacía, el sitio no muestra un bloque roto.

### RF-06 — Animaciones
- Entradas al aparecer en pantalla (títulos, botones y tarjetas), cinta de especialidades en movimiento, video opcional en la Portada, zoom ligado al scroll y capa al pasar el cursor sobre las tarjetas de proyecto.
- Se hacen con **CSS e `IntersectionObserver`**, sin librerías de animación. Solo se animan `transform` y `opacity`.
- Con "reducir movimiento" activo en el sistema, nada se mueve solo y todo el contenido es visible.

**Criterios de aceptación**
- [ ] Cada animación de entrada ocurre una sola vez y ningún contenido queda oculto si no llega a ejecutarse.
- [ ] Las animaciones no provocan saltos de diseño ni bajan Lighthouse Performance de 85 en móvil.

### RF-07 — Páginas legales
- Dos páginas editables desde el panel: `/terminos` y `/privacidad` (esta incluye tratamiento de datos y cookies).
- Los textos legales **no se inventan**: la estructura trae `[TEXTO PENDIENTE]` hasta que el cliente o su abogado los escriban.
- El formulario de cotización exige aceptar la política de privacidad, y el backend guarda la fecha de aceptación.
- El pie enlaza a las dos páginas y muestra "Desarrollado por Giltechnology".

**Criterios de aceptación**
- [ ] El backend rechaza una cotización sin la aceptación de la política de privacidad.
- [ ] Antes de publicar, no queda ningún `[TEXTO PENDIENTE]` en las páginas legales.

### Cambios de specs-001 (RF-08 a RF-12)
El detalle está en `specs/specs-001/requirements.md`. En resumen:
- **RF-08 — Hero con portadas de proyectos:** cada proyecto tiene la casilla "Mostrar en el hero"; con más de una portada rotan con un fundido, con una queda fija. Sustituye a los 3 destacados de RF-01. El título de la Portada queda vacío y el botón dice "Agenda una reunión".
- **RF-09 — Categorías:** la sección Proyectos del inicio muestra categorías (Comercial, Residencial, Corporativo) y `/proyectos` se filtra por categoría. Se mantiene "Ver todos los proyectos".
- **RF-10 — Dirección web automática:** el slug del proyecto se genera solo; con una sola palabra se le antepone "proyecto" (`proyecto-casa`).
- **RF-11 — WhatsApp en formato internacional:** `+58 412 730 5964`, calculado a partir del número.
- **RF-12 — Botón flotante de WhatsApp:** el icono clásico (círculo verde), abajo a la derecha, con el mensaje "Hola! quiero agendar una reunión".

### Cambios de specs-002 (RF-13 a RF-18)
El detalle está en `specs/specs-002/requirements.md`. En resumen:
- **RF-13 — Menú desplegable:** las opciones del menú van siempre detrás de un botón y se despliegan debajo del logo. El encabezado se oculta al bajar y vuelve al subir. "Cotiza tu proyecto" no cambia.
- **RF-14 — Botones del hero configurables:** dos interruptores en el panel para mostrarlos u ocultarlos.
- **RF-15 — Controles discretos en el hero:** una línea fina con indicadores, flechas y pausa, sin recuadros. No se quitan: lo que rota solo debe poder pararse.
- **RF-16 — Sin cintillo de especialidades:** deja de mostrarse en el inicio; la lista queda en el panel.
- **RF-17 — Área según el tipo de remodelación:** el formulario pide primero el tipo (las categorías) y muestra solo sus áreas. Todo configurable en el panel; un área sin categoría aparece en todos los tipos.
- **RF-18 — Contacto en una columna:** el formulario debajo del título y a todo el ancho; los datos de contacto debajo, en fila.

### Cambios de specs-003 (RF-19 a RF-33)
El detalle está en `specs/specs-003/requirements.md`. En resumen:
- **RF-19 — Tipografía desde el panel:** dos fuentes cargables (títulos y texto); vacías, se usan las originales.
- **RF-20 — Categorías visibles u ocultas:** una categoría oculta sale del inicio, del filtro y del formulario; sus proyectos siguen en "Todos".
- **RF-21 y RF-22 — Página de proyectos:** lleva el título de la sección, y las tarjetas muestran la descripción completa al pasar el mouse.
- **RF-23 y RF-24 — Servicios:** Proceso va antes que Servicios (el menú no cambia), y cada tarjeta de servicio tiene un botón "Cotizar".
- **RF-25 — Pasos y servicios:** se editan dentro de su sección en el panel.
- **RF-26 — Video en el hero:** es una portada más de la rotación.
- **RF-27 a RF-32 — Formulario:** varias áreas, cada una con sus m² (también escritos a mano); mensaje de WhatsApp sin emojis; estimado ocultable; títulos y textos de ejemplo editables; campos nuevos de fotos, visita y ubicación.
- **RF-33 — Pie de página:** iconos de WhatsApp, correo e Instagram; se quitan los datos de la sección Contacto.

---

## 5. Stack técnico

| Capa | Tecnología |
|---|---|
| Frontend | React + Vite, React Router, CSS con variables (tokens de la maqueta) |
| Backend | Django + Django REST Framework |
| Panel | Django Admin (+ `django-admin-sortable2` para ordenar) |
| Base de datos | PostgreSQL |
| Imágenes | Pillow |
| Entorno local | Docker Compose (backend, frontend, postgres) |

- Usa versiones **estables actuales** y **fíjalas** en `requirements.txt` y `package.json`.
- Diseño **mobile-first** y responsive.

### Despliegue (producción)

| Pieza | Dónde | Por qué |
|---|---|---|
| Frontend React | **Cloudflare Pages** | Sitio estático, CDN global, HTTPS automático, despliegue al hacer push |
| Imágenes y videos | **Cloudflare R2** (vía `django-storages`, compatible con S3) | Barato y sin costo por descarga; los archivos no viven en el servidor |
| Backend Django + panel | **Railway** (alternativa: VPS con Docker Compose) | Cloudflare no ejecuta Django + Postgres de forma práctica |
| PostgreSQL | Base de datos administrada del mismo proveedor del backend | Respaldos automáticos |
| DNS, proxy y firewall | **Cloudflare** | Protección DDoS y reglas de rate limit como capa extra |

- **El despliegue es una fase aparte, al final.** El cliente aún no tiene dominio. Mientras tanto se trabaja en local y, si hace falta mostrar avances, en las URLs gratuitas de cada servicio (`*.pages.dev`, `*.up.railway.app`).
- Ningún dominio va escrito en el código: todo sale de variables de `.env` (`ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, `MEDIA_URL`, `FRONTEND_URL`).
- Estructura de dominios para cuando se compre: `dominio.com` → Pages, `api.dominio.com` → backend, `media.dominio.com` → R2.
- En local, los archivos se guardan en disco (`media/`); en producción, en R2. Se cambia solo con variables de `.env`, sin tocar código.
- Videos: subirlos ya comprimidos (≤ 50 MB). Si en el futuro pesan mucho, evaluar Cloudflare Stream.

### Estructura de carpetas
```
/
├── AGENTS.md
├── README.md
├── .env.example
├── docker-compose.yml
├── docs/maqueta-legible.html   # + maqueta-original.html
├── specs/          # especificación base (requirements, design, tasks)
│   ├── specs-001/  # primer paquete de cambios del cliente (implementado)
│   ├── specs-002/  # segundo paquete de cambios (implementado)
│   └── specs-003/  # tercer paquete de cambios (implementado)
├── backend/        # Django (apps: core, projects, quotes, site_content)
└── frontend/       # React + Vite
```

### Comandos
```bash
docker compose up --build                              # levantar todo
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
docker compose exec backend python manage.py test      # tests backend
cd frontend && npm run lint && npm run build           # verificar frontend
cd frontend && npm test                                # tests frontend (Vitest)
```

### Errores del entorno
- Los errores que ya aparecieron (contenedores apagados, Docker cerrado, acceso al panel) y sus soluciones están en `docs/problemas-frecuentes.md`. Revísalo antes de diagnosticar desde cero.
- Si aparece un error nuevo de entorno o de comandos, **agrégalo a ese archivo** con su causa y su solución.

---

## 6. Seguridad

**Secretos**
- Todas las claves (`SECRET_KEY`, credenciales de BD, etc.) van en `.env`.
- `.env` está en `.gitignore`. Se versiona solo `.env.example` con valores de ejemplo.
- Nunca escribas un secreto en el código, en los logs ni en el frontend (todo lo que va al frontend es público).

**Rate limiting**
- API: throttling de DRF. Formulario de cotización: máx. **5 envíos por hora por IP**; resto de la API: límite general por IP.
- Login del panel: bloqueo tras intentos fallidos con `django-axes`.
- Campo *honeypot* oculto en el formulario contra bots.

**Configuración**
- Producción: `DEBUG=False`, `ALLOWED_HOSTS` y `CORS_ALLOWED_ORIGINS` explícitos, HTTPS, cookies seguras.
- URL del panel distinta de `/admin/` (configurable en `.env`).
- La API pública es **solo lectura**, excepto el endpoint de crear cotización.

**Archivos subidos**
- Validar extensión **y** tipo real del archivo, y tamaño máximo.
- Renombrar archivos al guardarlos (no usar el nombre original del usuario).

---

## 7. Calidad y definición de "terminado"

Una tarea está terminada cuando:
- [ ] Cumple sus criterios de aceptación de `specs/requirements.md`.
- [ ] Tiene tests para la lógica importante (cálculo de precio, límite de 3 destacados, validaciones, rate limit).
- [ ] `manage.py test`, `npm test`, `npm run lint` y `npm run build` pasan sin errores.
- [ ] Se ve bien en móvil y escritorio y se parece a la maqueta.
- [ ] Imágenes con `alt`, formulario usable con teclado.
- [ ] Las animaciones respetan `prefers-reduced-motion`.
- [ ] `specs/tasks.md` actualizado.

---

## 8. Lo que NO debes hacer

- No programes nada fuera de la spec aprobada.
- No cambies el stack ni agregues dependencias grandes sin preguntar.
- No subas `.env`, archivos de `media/` ni dumps de la base de datos al repositorio.
- No borres ni reescribas archivos que no tengan que ver con la tarea actual.
- No inventes textos, precios ni datos del cliente: usa los de la maqueta o marcadores claros como `[TEXTO PENDIENTE]`.

---

## 9. Formato de respuesta

Al terminar cada tarea o fase, responde con:
1. **Resumen** (3-4 líneas) de lo que creaste o cambiaste.
2. **Pasos para probarlo** (comandos y qué deberías ver).
3. **Decisiones tomadas por tu cuenta** que debo revisar, con el motivo.
4. **Pendientes o riesgos** detectados.

---

## 10. Decisiones confirmadas

| Tema | Decisión |
|---|---|
| Moneda | USD, con nota editable sobre ajustes y pago en bolívares a tasa BCV del día |
| Hosting | Cloudflare Pages (front) + R2 (media) + Railway o VPS (Django + Postgres) |
| Contenido | Todas las secciones editables desde el panel |
| WhatsApp | Enlace `wa.me`, y el mensaje se guarda en la base de datos |
| Dominio | Aún no comprado; se define en la fase de despliegue |
| Roles del panel | Admin (todo) y Viewer (solo lectura); por ahora un solo usuario Admin |
| Animaciones | Referencia: sparquitectosve.com, adaptada a la maqueta. Solo CSS, sin librerías |
| Páginas legales | Términos y Privacidad, editables en el panel y con `[TEXTO PENDIENTE]` hasta que el cliente dé los textos. Sin aviso de cookies: el sitio no las usa |
| Crédito | "Desarrollado por Giltechnology" fijo en el pie, sin enlace por ahora |
| Cambios del cliente | Van dentro de `specs/`, en paquetes numerados (`specs/specs-001/`…), que mandan sobre la base |
| Hero | Portadas de proyectos marcadas en el panel, con rotación; reemplaza a los destacados (specs-001) |
| Categorías | Comercial, Residencial y Corporativo; un proyecto pertenece a una (specs-001) |
| Menú | Siempre desplegable; el encabezado se oculta al bajar y vuelve al subir (specs-002) |
| Formulario | El área a remodelar depende del tipo de remodelación, que son las categorías (specs-002) |
| Especialidades | El cintillo se quitó del sitio; la lista se conserva en el panel (specs-002) |
| Cotización | Varias áreas por cotización, cada una con sus m²; el total es la suma (specs-003) |
| Mensaje de WhatsApp | Sin emojis: en algunas versiones llegaban como "?" (specs-003) |
| Tipografía | Dos fuentes cargables desde el panel, con las originales de respaldo (specs-003) |

## 11. Fases del proyecto

1. **Especificación:** `specs/` completo y aprobado.
2. **Backend:** modelos, panel, roles y API.
3. **Frontend:** maqueta convertida a React y conectada a la API.
4. **Calculadora y WhatsApp**, más las páginas legales.
5. **specs-001:** primer paquete de cambios del cliente (hero, categorías, dirección automática y WhatsApp). Implementado.
6. **specs-002:** segundo paquete (menú desplegable, hero, formulario por tipo de remodelación y sección Contacto). Implementado y cerrado el 2026-10-08.
7. **specs-003:** tercer paquete (tipografía, categorías ocultables, video en el hero, formulario con varias áreas y pie con iconos). Implementado y cerrado el 2026-10-09.
8. **specs-004:** cuarto paquete de cambios del cliente. **Es la fase siguiente; falta su especificación.**
9. **Despliegue:** dominio, Cloudflare (Pages, R2, DNS), Railway y checklist de seguridad en producción. **Pendiente, sin empezar.** Viene después de los paquetes de cambios.

**Preguntas abiertas** (si aparece una nueva, agrégala aquí y pregunta antes de decidir):

1. ¿El cliente quiere secciones **Nosotros** y **Testimonios**? No están en la maqueta; hoy están fuera de alcance (`specs/requirements.md` §6).
2. Los **textos legales** (Términos y Privacidad) los debe entregar el cliente o su abogado. Hasta entonces las páginas muestran `[TEXTO PENDIENTE]`; bloquea la publicación, no el desarrollo.

Ninguna bloquea el desarrollo.

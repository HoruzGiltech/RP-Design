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
├── specs/
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

## 11. Fases del proyecto

1. **Especificación:** `specs/` completo y aprobado.
2. **Backend:** modelos, panel, roles y API.
3. **Frontend:** maqueta convertida a React y conectada a la API.
4. **Calculadora y WhatsApp.**
5. **Despliegue:** dominio, Cloudflare (Pages, R2, DNS), Railway y checklist de seguridad en producción.

**Preguntas abiertas** (si aparece una nueva, agrégala aquí y pregunta antes de decidir):

1. ¿El cliente quiere secciones **Nosotros** y **Testimonios**? No están en la maqueta; hoy están fuera de alcance (`specs/requirements.md` §6).
2. Los **textos legales** (Términos y Privacidad) los debe entregar el cliente o su abogado. Hasta entonces las páginas muestran `[TEXTO PENDIENTE]`; bloquea la publicación, no el desarrollo.

No bloquea la Fase 2.

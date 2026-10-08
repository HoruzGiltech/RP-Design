# Requisitos — Web RP Design

> **Qué** se construye y **cómo sabemos que está bien hecho**.
> Fuente: `AGENTS.md`. Cualquier cambio de alcance se registra primero aquí.

**Estado:** Aprobado (v3, 2026-10-05) — incluye RF-06 Animaciones
**Maqueta:** `docs/maqueta-legible.html` (para leer y comparar) · `docs/maqueta-original.html` (archivo original del diseñador)
**Referencia de animaciones:** https://sparquitectosve.com/ (solo el movimiento; el aspecto sigue siendo el de la maqueta)

> ⚠️ **Parte de este documento quedó sustituida por `specs/specs-001/requirements.md`** (cambios del cliente, ya implementados). No programes sobre estos apartados sin leer el paquete:
> - **S2 Portada** y **RF-06.2, RF-06.5, RF-06.6 en la Portada** → hero con portadas de proyectos que rotan (RF-08).
> - **S5 Proyectos**, **RF-01.1**, **CA-01.1** y **CA-01.2** (los 3 destacados) → tarjetas de categorías (RF-09). Ya no existen los "destacados".
> - **Campo de texto "categoría"** del proyecto → relación con la lista de categorías (RF-09.2).
> - **Dirección web editable** del proyecto → se genera sola (RF-10).
> - **"WhatsApp como se muestra"** de RF-04.5 → se calcula en formato internacional (RF-11).
> - Se agrega el **botón flotante de WhatsApp** (RF-12).
>
> ⚠️ **Y otra parte quedó sustituida por `specs/specs-002/requirements.md`** (segundo paquete, ya implementado):
> - **S1 Encabezado** → menú siempre desplegable y encabezado que se oculta al bajar (RF-13).
> - **S3 Franja de especialidades** y **RF-06.4** → eliminadas del sitio (RF-16). La lista sigue en el panel.
> - **RF-03.2** (lista única de áreas) → áreas según el tipo de remodelación (RF-17).
> - **S7 Contacto** y **RF-03.11** → una sola columna, con el formulario a todo el ancho (RF-18).

---

## 1. Objetivo

Sitio web tipo **portafolio** para RP Design (diseño de interiores y obras), donde **Proyectos** es la sección protagonista. Incluye:

- Una calculadora de cotización que envía los datos por WhatsApp.
- Un panel donde el cliente mantiene todo el contenido sin tocar código.

## 2. Usuarios

| Usuario | Qué necesita |
|---|---|
| **Visitante** | Ver proyectos, conocer la empresa y pedir una cotización desde el celular o la computadora |
| **Admin** (cliente) | Gestionar todo el contenido, los precios y las cotizaciones recibidas |
| **Viewer** | Consultar el contenido y las cotizaciones sin poder modificar nada |

---

## 3. Inventario de secciones del sitio

Validado contra la maqueta. Página única con anclas: `#inicio`, `#servicios`, `#proyectos`, `#proceso` y `#contacto`.

| # | Sección (ancla) | Tipo | Contenido en la maqueta | Campos editables |
|---|---|---|---|---|
| S1 | Encabezado | Única (en SiteSettings) | Logo circular "RP", "RP DISEÑO" / "INTERIOR · ARQUITECTURA", menú Servicios · Proyectos · Proceso y botón "Cotiza tu proyecto" | Logo (imagen opcional; si no hay, se dibuja el círculo con las iniciales), iniciales, nombre, subtítulo, texto del botón. Los enlaces del menú son fijos. El **icono de la pestaña (favicon)** usa el mismo logo; si no hay, el círculo con las iniciales |
| S2 | Portada `#inicio` | Única | Antetítulo "ESTUDIO DE DISEÑO DE INTERIORES · CARACAS", H1, párrafo, botones "Agenda una visita" y "Ver proyectos", foto principal | Antetítulo, título, párrafo, textos de los 2 botones, imagen principal y su `alt`, **video opcional** (RF-06.5) |
| S3 | Franja de especialidades | Lista | Diseño residencial · Diseño comercial · Renders 3D · Ejecución de obra | Texto de cada ítem y orden. Se muestra como cinta en movimiento (RF-06.4) |
| S4 | Servicios `#servicios` | Única + lista | Título "Un solo equipo para todo tu proyecto", intro y 3 tarjetas numeradas 01–03 | Título, intro. Por tarjeta: título y descripción. **El número (01, 02…) se genera según el orden** |
| S5 | Proyectos `#proyectos` | Única + dinámica | Fondo oscuro, título "Proyectos recientes", enlace "Ver más en Instagram", 3 tarjetas (foto, categoría, título, resumen) | Título, texto del enlace a Instagram, texto del botón "Ver todos". Las tarjetas salen de los proyectos destacados (RF-01) |
| S6 | Proceso `#proceso` | Única + lista | Título "Ve tu espacio antes de construirlo", intro, video recorrido y 4 entregables A–D | Título, intro, video y su poster. Por entregable: título y descripción. **La letra (A, B…) se genera según el orden** |
| S7 | Contacto `#contacto` | Única + RF-03 | Título "Cuéntanos sobre tu espacio", intro, datos de contacto y formulario | Título, intro, texto del botón de envío. Los datos de contacto salen de SiteSettings |
| S8 | Pie de página | Única | "RP DISEÑO INTERIOR", "Arquitectura · Interiorismo · Remodelaciones — Caracas", © año | Nombre y lema. **El año se calcula solo**. Segunda fila: enlaces a las páginas legales (RF-07) y el crédito fijo "Desarrollado por Giltechnology" |
| S9 | SEO | Única (no visible) | — | Título del sitio, descripción, imagen para compartir |

**Datos reales que trae la maqueta** (se cargan como datos iniciales, **no** van escritos en el código):
- WhatsApp: `584127305964` (mostrado como "0412 730 5964")
- Correo: `rpdesings05@gmail.com` (confirmado por el cliente el 2026-10-06)
- Instagram: `@rpdesign_ve`
- Ciudad: Caracas, Venezuela

**Elementos que se agregan y no están en la maqueta:**
- Botón **"Ver todos los proyectos"** en S5 (RF-01.2).
- Páginas `/proyectos` y `/proyectos/<slug>`, que se diseñan con el mismo estilo de S5 (fondo oscuro, tarjetas iguales).
- Campos **correo**, **área** y **m²** y el **estimado** en el formulario de S7 (RF-03).
- **Menú hamburguesa** en móvil: la maqueta solo hace que el menú pase a varias líneas.
- **Animaciones** (RF-06): la maqueta es estática; el movimiento se toma de la página de referencia.

---

## 4. Requisitos funcionales

### RF-01 — Proyectos

| ID | Requisito |
|---|---|
| RF-01.1 | El inicio muestra los proyectos **destacados** (máx. 3) en el orden definido en el panel |
| RF-01.2 | El botón "Ver todos los proyectos" lleva a `/proyectos`, con una cuadrícula de miniaturas de todos los proyectos publicados |
| RF-01.3 | Cada proyecto tiene su página `/proyectos/<slug>` con galería, descripción, categoría, ubicación y año |
| RF-01.4 | Solo se muestran proyectos **publicados** |
| RF-01.5 | La cuadrícula respeta el orden definido en el panel |

**Criterios de aceptación**
- [ ] CA-01.1 El panel impide marcar un 4.º proyecto destacado y muestra un mensaje claro.
- [ ] CA-01.2 Con 0, 1 o 2 destacados, el inicio no muestra huecos ni bloques rotos (con 0, la sección se oculta).
- [ ] CA-01.3 Un proyecto en borrador da **404** en su URL pública.
- [ ] CA-01.4 La URL de un proyecto se puede copiar, abrir en otra pestaña y el botón "atrás" funciona.
- [ ] CA-01.5 Un slug que no existe muestra una página 404 amigable.

### RF-02 — Multimedia

| ID | Requisito |
|---|---|
| RF-02.1 | Cada proyecto tiene una **imagen de portada** obligatoria |
| RF-02.2 | Cada proyecto tiene una galería de **imágenes y videos**, que se ordenan arrastrando |
| RF-02.3 | Imágenes permitidas: `jpg`, `jpeg`, `png`, `webp`, de hasta **5 MB** |
| RF-02.4 | Videos permitidos: `mp4`, `webm`, de hasta **50 MB** |
| RF-02.5 | Al subir una imagen se genera una versión optimizada (máx. 1920 px) y una miniatura (600 px) |
| RF-02.6 | Cada video puede tener una imagen **poster**; los videos no se reproducen solos con sonido |
| RF-02.7 | Cada archivo tiene un texto alternativo (`alt`) |

**Criterios de aceptación**
- [ ] CA-02.1 Un archivo con extensión válida pero contenido falso (ej. `.exe` renombrado a `.jpg`) se rechaza.
- [ ] CA-02.2 Un archivo que supera el tamaño máximo se rechaza con un mensaje que indica el límite.
- [ ] CA-02.3 La cuadrícula de proyectos carga miniaturas, no las imágenes originales.
- [ ] CA-02.4 Los límites de tamaño se cambian desde `.env`.

### RF-03 — Calculadora de cotización y WhatsApp

| ID | Requisito |
|---|---|
| RF-03.1 | Campos obligatorios: nombre, correo, teléfono, área, m² y la **casilla de aceptación de la política de privacidad** (RF-07.4). Campo opcional: mensaje |
| RF-03.2 | Áreas: baño, cocina, sala, patio, piscina y otro. Si se elige "otro", aparece un campo obligatorio para especificarla |
| RF-03.3 | Las áreas y su **precio por m² en USD** se gestionan en el panel |
| RF-03.4 | El estimado se calcula en vivo como `m² × precio_por_m²` |
| RF-03.5 | Si el área es "otro" o no tiene precio, se muestra **"A cotizar"** |
| RF-03.6 | El formato del precio es `USD 1.250,00` |
| RF-03.7 | Bajo el monto se muestra la **nota de precio**, editable en el panel (texto por defecto en `design.md`) |
| RF-03.8 | Al enviar, el backend valida, **recalcula** el precio, arma el mensaje, guarda la cotización **con el texto exacto del mensaje** y devuelve el enlace `wa.me` |
| RF-03.9 | El frontend abre WhatsApp con ese enlace, dirigido al número configurado en el panel |
| RF-03.10 | Los m² se eligen con un **control deslizante** (una línea con un botón que se arrastra), de 1 m² hasta el máximo configurable en el panel (500 m² por defecto; quien necesite más lo conversa con RP Design), de metro en metro. El valor elegido se ve junto a la etiqueta y el estimado cambia mientras se arrastra |
| RF-03.11 | El formulario mantiene el estilo de la maqueta (caja clara con borde, etiquetas en negrita, inputs blancos). Orden de los campos: Nombre, Teléfono, Correo, Área a remodelar, Metros cuadrados, Estimado, Mensaje. El botón dice **"Enviar por WhatsApp"** |
| RF-03.12 | El campo "Tipo de proyecto" de la maqueta (Residencial / Comercial / Solo renders o planos / Ejecución de obra) **se reemplaza** por "Área a remodelar", que es el que define el precio |

**Criterios de aceptación**
- [ ] CA-03.1 El mensaje incluye: nombre, correo, teléfono, área, m², estimado (o "A cotizar") y mensaje.
- [ ] CA-03.2 Si alguien manipula el precio en el navegador, el valor guardado y el que aparece en el mensaje siguen siendo los que calcula el backend.
- [ ] CA-03.3 Cambiar un precio o la nota en el panel se refleja en el sitio al recargar.
- [ ] CA-03.4 Cada envío aparece en el panel con fecha, datos, mensaje completo y estado `nuevo`.
- [ ] CA-03.5 Si el navegador bloquea la apertura de WhatsApp, se muestra un botón "Abrir WhatsApp" para hacerlo a mano.
- [ ] CA-03.6 Los errores de validación se muestran junto a cada campo, en español.

### RF-04 — Panel de administración

| ID | Requisito |
|---|---|
| RF-04.1 | El panel es Django Admin, en español, con una URL configurable (no `/admin/`) |
| RF-04.2 | CRUD de proyectos, con publicar/despublicar y ordenar arrastrando |
| RF-04.3 | La galería de cada proyecto se gestiona y ordena dentro del mismo proyecto |
| RF-04.4 | Gestión de áreas y precios por m² |
| RF-04.5 | Configuración general: marca (nombre, subtítulo, iniciales, logo), WhatsApp, correo, Instagram, ciudad, nota de precio, máximo de m² y **color de acento** (una de las 4 opciones que trae la maqueta) |
| RF-04.6 | Edición de todas las secciones (RF-05) |
| RF-04.7 | Listado de cotizaciones con filtros por estado, área y fecha, búsqueda por nombre, correo o teléfono, y cambio de estado |
| RF-04.8 | Dos roles: **Admin** (todo) y **Viewer** (solo lectura). Se crean automáticamente al migrar |

**Criterios de aceptación**
- [ ] CA-04.1 Un Viewer puede ver todo, pero no ve los botones de guardar, eliminar ni ordenar.
- [ ] CA-04.2 Si un Viewer intenta una acción por URL o POST directo, recibe un error 403.
- [ ] CA-04.3 Los grupos Admin y Viewer existen después de `migrate` en una base de datos vacía.
- [ ] CA-04.4 Hay tests automáticos de permisos para cada rol.

### RF-05 — Contenido editable

| ID | Requisito |
|---|---|
| RF-05.1 | Todas las secciones del inventario (§3) se editan desde el panel |
| RF-05.2 | Las secciones **únicas** no se pueden crear de nuevo ni eliminar, solo editar |
| RF-05.3 | Las secciones de tipo **lista** permiten agregar, editar, ordenar y ocultar elementos |
| RF-05.4 | Cada sección tiene el interruptor "Mostrar en el sitio" |
| RF-05.5 | El frontend no tiene textos ni imágenes del cliente escritos a mano |

**Criterios de aceptación**
- [ ] CA-05.1 Un cambio en el panel se ve en el sitio al recargar, sin redeploy.
- [ ] CA-05.2 Una sección oculta o vacía no deja un bloque roto ni un título suelto.
- [ ] CA-05.3 Con la base de datos recién creada, el sitio carga sin errores y muestra **los mismos textos de la maqueta** (datos iniciales). Donde la maqueta no tiene imagen se muestra un recuadro gris neutro, sin el texto `[FOTO…]`.
- [ ] CA-05.4 Cambiar el color de acento en el panel cambia los botones principales y los números de Servicios.

### RF-07 — Páginas legales

| ID | Requisito |
|---|---|
| RF-07.1 | Dos páginas: `/terminos` (Términos y condiciones) y `/privacidad` (Política de privacidad, que incluye el tratamiento de datos y el uso de cookies) |
| RF-07.2 | Cada página tiene título, introducción y una lista de apartados (subtítulo y texto) que el cliente agrega, edita y ordena en el panel. Las páginas no se pueden crear ni eliminar |
| RF-07.3 | Los textos legales **no se inventan**: la estructura inicial trae los subtítulos como guía y `[TEXTO PENDIENTE]` en cada texto. Los escribe el cliente o su abogado |
| RF-07.4 | El formulario de cotización tiene una casilla obligatoria "Acepto la política de privacidad…" con enlace a `/privacidad`. Sin marcarla no se envía, y el backend guarda la fecha de aceptación con cada cotización |
| RF-07.5 | El pie de página enlaza a las dos páginas y muestra el crédito "Desarrollado por Giltechnology" (texto fijo, sin enlace por ahora) |
| RF-07.6 | Cada página muestra la fecha de su última actualización, que cambia sola al editarla |

**Criterios de aceptación**
- [ ] CA-07.1 Con la base de datos recién creada existen las dos páginas, con sus apartados y `[TEXTO PENDIENTE]`.
- [ ] CA-07.2 Un cambio en el panel se ve en la página al recargar, y la fecha de actualización cambia.
- [ ] CA-07.3 Si alguien envía la cotización sin la aceptación (también por fuera del formulario), el backend la rechaza.
- [ ] CA-07.4 Antes de publicar el sitio no queda ningún `[TEXTO PENDIENTE]` en las páginas legales.

**Cookies:** el sitio público no usa cookies propias ni de terceros (no hay analítica ni publicidad), así que no lleva aviso de cookies. Las únicas cookies son las del panel, para la sesión del cliente. Si más adelante se agrega analítica, habrá que añadir el aviso y actualizar la política.

### RF-06 — Animaciones

La maqueta no tiene movimiento. Se toma como referencia https://sparquitectosve.com/ y se adapta al estilo de la maqueta (sobrio, recto, sin sombras). **La maqueta sigue mandando en colores, tipografías, espaciados y distribución**; de la referencia solo se toma cómo aparecen y reaccionan los elementos.

| ID | En la referencia | En RP Design |
|---|---|---|
| RF-06.1 | Títulos y textos aparecen subiendo con fundido al entrar en pantalla | Igual, en el antetítulo, título e intro de cada sección (S2, S4, S5, S6, S7) y en las páginas de proyectos |
| RF-06.2 | Los botones entran desde un lado | Los dos botones de la Portada entran desde la derecha, después del título |
| RF-06.3 | Las 3 tarjetas entran desde la izquierda, desde abajo y desde la derecha | Igual en las tarjetas de Servicios en escritorio. En móvil, y en las tarjetas de Proyectos y los pasos de Proceso, entran desde abajo, una tras otra |
| RF-06.4 | Carrusel que avanza solo y se pausa al pasar el cursor | La franja de especialidades (S3) pasa a ser una cinta continua que se pausa con el cursor o el foco |
| RF-06.5 | Portada con video de fondo en bucle, sin sonido | La Portada acepta un **video opcional** que se reproduce en bucle y sin sonido dentro del mismo recuadro de la foto. La foto queda como vista previa |
| RF-06.6 | Fondo que hace zoom mientras se baja la página | Zoom suave ligado al scroll en la imagen de la Portada y en la portada del detalle de proyecto |
| RF-06.7 | En la galería, una capa oscura aparece sobre la foto al pasar el cursor | Igual en las tarjetas de proyecto: capa oscura con "Ver proyecto" y un zoom leve de la foto |
| RF-06.8 | — | Las animaciones de entrada ocurren **una sola vez** por elemento |
| RF-06.9 | — | Con "reducir movimiento" activo en el sistema, no hay desplazamientos, cinta, zoom ni video automático: todo se ve en su estado final |

**No se toma de la referencia:**
- Tarjetas que se voltean al pasar el cursor: esconden el texto del servicio y no funcionan en pantallas táctiles.
- Video de fondo detrás del formulario de contacto: baja el contraste del formulario y pesa en móvil.
- Formulario por pasos: el de RP Design es corto y ya está definido en RF-03.

**Criterios de aceptación**
- [ ] CA-06.1 Al bajar por el inicio, cada sección aparece con su animación una vez y no se repite al volver a subir.
- [ ] CA-06.2 Con "reducir movimiento" activo, todo el contenido es visible y nada se mueve solo.
- [ ] CA-06.3 Ningún contenido queda oculto si la animación no llega a ejecutarse.
- [ ] CA-06.4 La cinta de especialidades se detiene con el cursor encima o con el foco del teclado, y un lector de pantalla lee cada especialidad una sola vez.
- [ ] CA-06.5 Sin video en la Portada, se muestra la imagen (o el recuadro gris) como hasta ahora.
- [ ] CA-06.6 Las animaciones no mueven el resto de la página (sin saltos de diseño) y Lighthouse Performance se mantiene ≥ 85 en móvil.

---

## 5. Requisitos no funcionales

| ID | Requisito |
|---|---|
| RNF-01 | **Responsive y mobile-first**: se ve bien de 360 px a 1920 px de ancho |
| RNF-02 | **Fidelidad visual**: los colores, tipografías y espaciados salen de los tokens extraídos de la maqueta |
| RNF-03 | **Rendimiento**: imágenes con carga diferida (`loading="lazy"`), miniaturas en la cuadrícula y Lighthouse Performance ≥ 85 en móvil |
| RNF-04 | **Accesibilidad**: `alt` en todas las imágenes, formulario usable con teclado y contraste AA |
| RNF-05 | **Seguridad**: secretos en `.env`, rate limit, protección del login, validación de archivos y `DEBUG=False` en producción |
| RNF-06 | **Idioma**: interfaz y panel en español; código en inglés |
| RNF-07 | **Navegadores**: las dos últimas versiones de Chrome, Safari, Firefox y Edge, incluidos Safari iOS y Chrome Android |
| RNF-08 | **Portabilidad**: ningún dominio ni secreto escrito en el código; todo sale de variables de entorno |

### Rate limit

| Recurso | Límite |
|---|---|
| `POST /api/quotes/` | 5 por hora por IP |
| Resto de la API pública | 120 por minuto por IP |
| Login del panel | Bloqueo de 30 min tras 5 intentos fallidos |

---

## 6. Fuera de alcance (por ahora)

- API oficial de WhatsApp Business (envío automático).
- Conversión automática a bolívares.
- Sitio en varios idiomas.
- Blog, pagos en línea o cuentas de usuario para visitantes.
- Librerías de animación (GSAP, AOS, Swiper, Framer Motion): las animaciones de RF-06 se hacen con CSS.
- Secciones **Nosotros** y **Testimonios**: no están en la maqueta. **Pendiente de preguntar al cliente** (T-1.4b); si las quiere, se diseñan y se agregan como un cambio de alcance.
- Compra del dominio y despliegue (se hacen en la fase 5).

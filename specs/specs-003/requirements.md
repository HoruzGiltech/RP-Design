# Requisitos — specs-003: tercera ronda de cambios del cliente

> **Qué** cambia respecto a lo ya construido y **cómo sabemos que está bien hecho**.
> Es un paquete de cambios sobre `specs/`, `specs/specs-001/` y `specs/specs-002/`. Donde este documento los contradice, **manda este**.

**Estado:** Implementado y cerrado (2026-10-09)

> ⚠️ **Tres puntos quedaron sustituidos por `specs/specs-004/requirements.md`:** RF-24 (botón "Cotizar" bajo el texto de la tarjeta) → dentro de la capa sobre la portada (RF-37); P-25 ("Cotizar" siempre visible en celular) → entra al aparecer la tarjeta (RF-41); y el orden de los campos del formulario → "Tengo fotos" va arriba del mensaje (RF-40). El resto de este paquete sigue vigente.
**Base:** `specs/` (RF-01 a RF-07), `specs/specs-001/` (RF-08 a RF-12) y `specs/specs-002/` (RF-13 a RF-18), ya implementadas y cerradas.
**Reglas:** las mismas de `AGENTS.md`: mismo stack, mismos tokens de diseño, SDD, tests, accesibilidad y animaciones solo con CSS.

> ⚠️ **El despliegue sigue pendiente y sin empezar.** Es la última fase del proyecto (`specs/tasks.md`, Fase 5) y viene después de este paquete. Ver §7.

---

## 1. Resumen de los cambios

| # | Pedido del cliente | Requisito |
|---|---|---|
| 1 | Cargar la tipografía desde el panel y que el sitio cambie solo | RF-19 |
| 2 | Casilla para mostrar u ocultar cada categoría | RF-20 |
| 3 | La página de proyectos lleva el mismo nombre que la sección | RF-21 |
| 4 | La descripción del proyecto se ve sobre la portada al pasar el mouse | RF-22 |
| 5 | Intercambiar el orden de Servicios y Proceso | RF-23 |
| 6 | Botón "Cotizar" al pasar el mouse por una tarjeta de Servicios | RF-24 |
| 7 | Poder editar los pasos del proceso | RF-25 |
| 8 | Que el video del hero rote con las imágenes | RF-26 |
| 9 | Elegir más de un área a remodelar | RF-27 |
| 10 | Emojis del mensaje de WhatsApp que llegan como "?" | RF-28 |
| 11 | Escribir los m² a mano y que la barra se mueva | RF-29 |
| 12 | Mostrar u ocultar el cálculo de precio | RF-30 |
| 13 | Títulos y textos de ejemplo del formulario editables | RF-31 |
| 14 | Casilla "tengo fotos del espacio" | RF-32 |
| 15 | Casilla "no sé cuántos m² son, agendar una visita" | RF-32 |
| 16 | Campo "ubicación del espacio" | RF-32 |
| 17 | Iconos de WhatsApp, correo e Instagram en el pie, y quitarlos de Contacto | RF-33 |

### Respuesta a las tres consultas de factibilidad

| Consulta | Respuesta |
|---|---|
| Cargar la tipografía desde el panel | **Factible** (RF-19), con tres límites que se explican allí: pesos de la fuente, un parpadeo al cargar y la licencia |
| Descripción sobre la portada al pasar el mouse | **Factible** (RF-22). En celulares no hay "pasar el mouse", y una descripción larga necesita scroll dentro de la foto |
| ¿El video rota con las imágenes del hero? | **Hoy no:** solo se usa de respaldo si ningún proyecto está marcado para el hero. RF-26 lo cambia |

---

## 2. Requisitos funcionales

### RF-19 — Tipografía cargable desde el panel

| ID | Requisito |
|---|---|
| RF-19.1 | En "Configuración general" hay dos archivos opcionales: **"Fuente de títulos"** y **"Fuente de texto"** |
| RF-19.2 | Al cargar una fuente, el sitio la usa en lugar de la actual, sin redeploy. Si un campo está vacío, se usa la fuente original (Archivo Narrow para títulos, Archivo para texto) |
| RF-19.3 | Formatos admitidos: `woff2`, `woff`, `ttf` y `otf`, hasta **2 MB** (configurable en `.env`). Se valida extensión, tamaño y contenido real, y el archivo se renombra al guardarlo |
| RF-19.4 | El panel explica que conviene una **fuente variable** (un archivo con todos los grosores) y que el cliente debe tener licencia para usarla en la web |
| RF-19.5 | Si la fuente no carga (archivo borrado, sin conexión), el sitio se ve con la fuente original, nunca sin texto |

**Límites conocidos** (no son defectos; quedan aquí para explicárselos al cliente):
- **Pesos:** el sitio usa varios grosores (400 a 800). Con un archivo de un solo grosor, el navegador simula las negritas y se ven peor.
- **Parpadeo:** la fuente llega después de que la página empieza a dibujarse, así que el texto se ve un instante con la fuente original.

**Criterios de aceptación**
- [ ] CA-19.1 Un archivo con extensión de fuente pero contenido falso se rechaza, y también uno que pasa del tamaño máximo.
- [ ] CA-19.2 Con una fuente cargada en "títulos", los títulos del sitio cambian y el texto no. Y al revés.
- [ ] CA-19.3 Al quitar la fuente en el panel, el sitio vuelve a la original al recargar.
- [ ] CA-19.4 Mientras la fuente carga, el texto es visible.

### RF-20 — Categorías visibles u ocultas

| ID | Requisito |
|---|---|
| RF-20.1 | Cada categoría tiene la casilla **"Mostrar en el sitio"**, activada por defecto y editable desde la lista del panel |
| RF-20.2 | Una categoría oculta no aparece en: las tarjetas de la sección Proyectos del inicio, el filtro de `/proyectos`, ni el "Tipo de remodelación" del formulario |
| RF-20.3 | Los **proyectos** de una categoría oculta **siguen viéndose** en "Todos", en el hero y en su página, con su etiqueta de categoría |
| RF-20.4 | `/proyectos?categoria=<una oculta>` muestra todos los proyectos, igual que una categoría que no existe |

**Criterios de aceptación**
- [ ] CA-20.1 Ocultar una categoría la quita de los tres sitios de RF-20.2 al recargar.
- [ ] CA-20.2 Su proyecto sigue apareciendo en "Todos".
- [ ] CA-20.3 El backend rechaza una cotización cuyo tipo es una categoría oculta.

### RF-21 — La página de proyectos usa el nombre de la sección

| ID | Requisito |
|---|---|
| RF-21.1 | El título de `/proyectos` es el **título de la sección Proyectos** del panel (hoy "Mis Proyectos"), no el texto fijo "Proyectos" |
| RF-21.2 | El título de la pestaña del navegador usa ese mismo texto |
| RF-21.3 | Con un filtro de categoría, el título sigue siendo el nombre de la categoría, como ahora |

**Criterios de aceptación**
- [ ] CA-21.1 Cambiar el título de la sección en el panel cambia el de `/proyectos` al recargar.

### RF-22 — Descripción del proyecto sobre la portada

Cambia RF-06.7 de `specs/` (la capa decía solo "Ver proyecto").

| ID | Requisito |
|---|---|
| RF-22.1 | En las tarjetas de proyecto, al pasar el mouse o al enfocarlas con el teclado, sobre la foto aparece la **descripción completa** del proyecto |
| RF-22.2 | Si la descripción es más larga que la foto, se puede desplazar dentro de la capa. No se recorta |
| RF-22.3 | La tarjeta sigue siendo un enlace a la página del proyecto |
| RF-22.4 | En pantallas táctiles la capa no aparece: la tarjeta se ve como hoy y la descripción se lee en la página del proyecto |

**Criterios de aceptación**
- [ ] CA-22.1 Con una descripción de varios párrafos, todo el texto es accesible desplazando dentro de la foto.
- [ ] CA-22.2 El texto sobre la foto cumple contraste AA.
- [ ] CA-22.3 Se respetan los saltos de línea que escribió el cliente.

### RF-23 — Proceso antes que Servicios

| ID | Requisito |
|---|---|
| RF-23.1 | El orden del inicio pasa a: Hero → Proyectos → **Proceso → Servicios** → Contacto |
| RF-23.2 | **El menú desplegable no cambia** de orden: Servicios, Proyectos, Proceso |

### RF-24 — Botón "Cotizar" en Servicios

| ID | Requisito |
|---|---|
| RF-24.1 | Al pasar el mouse por una tarjeta de servicio, o al llegar a ella con el teclado, aparece un botón **"Cotizar"** que lleva al formulario de contacto |
| RF-24.2 | En pantallas táctiles el botón se muestra siempre |
| RF-24.3 | El texto del botón se edita en "Servicios (encabezado)" del panel |
| RF-24.4 | Si la sección Contacto está oculta, el botón no se muestra |

**Criterios de aceptación**
- [ ] CA-24.1 Que aparezca el botón no cambia el tamaño de la tarjeta ni mueve el resto de la página.
- [ ] CA-24.2 El botón se alcanza y se activa con el teclado.

### RF-25 — Pasos del proceso y servicios dentro de su sección

Los pasos y los servicios **ya eran editables**: estaban en listas aparte del menú del panel ("Pasos del proceso" y "Servicios"), por eso no se veían al abrir la sección.

| ID | Requisito |
|---|---|
| RF-25.1 | Los **pasos** se agregan, editan, ordenan y ocultan **dentro de "Proceso (encabezado)"** |
| RF-25.2 | Los **servicios**, dentro de "Servicios (encabezado)" |
| RF-25.3 | Las entradas sueltas "Pasos del proceso" y "Servicios" desaparecen del menú del panel |
| RF-25.4 | No se pierde ningún paso ni servicio existente |

**Criterios de aceptación**
- [ ] CA-25.1 Al abrir "Proceso (encabezado)" se ven el título, la introducción, el video y la tabla de pasos.
- [ ] CA-25.2 Reordenar los pasos arrastrando cambia las letras A, B, C… en el sitio.

### RF-26 — El video como una portada más del hero

Cambia RF-08.9 de specs-001 (el video era solo un respaldo).

| ID | Requisito |
|---|---|
| RF-26.1 | El video de "Portada" entra en la rotación del hero junto con las portadas de los proyectos, como **primera** portada |
| RF-26.2 | Se reproduce sin sonido. Cuando termina, pasa a la siguiente portada |
| RF-26.3 | Se maneja con los mismos controles: anterior, siguiente, pausa e indicador |
| RF-26.4 | Con "reducir movimiento" el video no se reproduce: en su lugar se muestra la imagen de respaldo de la Portada, o se omite si no hay |
| RF-26.5 | Si no hay ningún proyecto marcado para el hero, el video sigue mostrándose solo, en bucle, como hasta ahora |

**Criterios de aceptación**
- [ ] CA-26.1 Con un video y dos proyectos, el hero muestra tres portadas y pasa del video a la primera imagen al terminar.
- [ ] CA-26.2 Pausar detiene también el video.
- [ ] CA-26.3 Al volver al video desde otra portada, empieza desde el principio.

### RF-27 — Varias áreas a remodelar

Cambia RF-17.2 de specs-002 y RF-03.4 de `specs/`.

| ID | Requisito |
|---|---|
| RF-27.1 | "Área a remodelar" pasa de un desplegable a una lista de **casillas**: se marcan una o varias áreas del tipo elegido |
| RF-27.2 | **Cada área marcada pide sus propios m²** |
| RF-27.3 | El estimado de cada área es `m² × su precio`, y el **estimado total es la suma** |
| RF-27.4 | Si alguna de las áreas marcadas no tiene precio (o es "Otro"), el total es **"A cotizar"** |
| RF-27.5 | "Otro" sigue pidiendo un texto para especificar el área |
| RF-27.6 | Hay que marcar al menos un área |
| RF-27.7 | La cotización guarda un renglón por área, con sus m², el precio usado y su subtotal. En el panel se ven como una tabla |
| RF-27.8 | Las cotizaciones anteriores se conservan, convertidas a cotizaciones de un solo renglón |

**Criterios de aceptación**
- [ ] CA-27.1 Con Cocina (100 USD/m², 10 m²) y Baño (80 USD/m², 5 m²), el total es `USD 1.400,00`.
- [ ] CA-27.2 Al cambiar de tipo de remodelación, las áreas marcadas se borran.
- [ ] CA-27.3 El backend recalcula cada subtotal y el total; ignora cualquier monto enviado por el navegador.
- [ ] CA-27.4 El backend rechaza un área que no pertenece al tipo, y una cotización sin áreas.
- [ ] CA-27.5 El mensaje de WhatsApp lista cada área con sus m².

### RF-28 — Mensaje de WhatsApp sin emojis

| ID | Requisito |
|---|---|
| RF-28.1 | El mensaje no lleva emojis. Cada dato empieza con un guion: `- Nombre: Ana Pérez` |
| RF-28.2 | El contenido del mensaje no se pierde: mismos datos, más los campos nuevos de este paquete |

**Causa probable de los "?":** algunas versiones de WhatsApp, sobre todo en computadora, no interpretan los emojis cuando llegan dentro de un enlace. Con texto simple el mensaje se lee igual en todas.

**Criterios de aceptación**
- [ ] CA-28.1 El mensaje guardado y el del enlace no contienen ningún emoji.

### RF-29 — Metros cuadrados escritos a mano

| ID | Requisito |
|---|---|
| RF-29.1 | Junto a la barra de m² hay un **campo numérico**: escribir un número mueve la barra, y mover la barra cambia el número |
| RF-29.2 | El campo admite decimales (`12,5`). La barra avanza de metro en metro |
| RF-29.3 | Un número fuera del rango (menor que 1 o mayor que el máximo del panel) muestra un error, y la barra se queda en el extremo |

**Criterios de aceptación**
- [ ] CA-29.1 Escribir `120` mueve la barra a 120; mover la barra a 45 pone `45` en el campo.
- [ ] CA-29.2 El estimado cambia al escribir, igual que al mover la barra.

### RF-30 — Mostrar u ocultar el cálculo de precio

| ID | Requisito |
|---|---|
| RF-30.1 | Interruptor **"Mostrar el estimado de precio"** en "Configuración general", activado por defecto |
| RF-30.2 | Apagado, el visitante no ve el estimado ni la nota de precio: ni en el formulario, ni en la pantalla de confirmación, ni en el mensaje de WhatsApp |
| RF-30.3 | El backend **sigue calculando y guardando** el estimado: RP Design lo ve en cada cotización del panel |

**Criterios de aceptación**
- [ ] CA-30.1 Con el interruptor apagado, la respuesta de la API al enviar no trae el monto, y el mensaje no tiene la línea del estimado.
- [ ] CA-30.2 Esa cotización, en el panel, sí muestra su estimado.

### RF-31 — Títulos y textos de ejemplo del formulario editables

| ID | Requisito |
|---|---|
| RF-31.1 | En "Contacto" del panel hay una tabla **"Campos del formulario"**: una fila por campo, con su **título** y su **texto de ejemplo** |
| RF-31.2 | Las filas son fijas: no se agregan ni se borran. Se crean solas con los textos actuales |
| RF-31.3 | El sitio usa esos textos al recargar |
| RF-31.4 | El texto de la casilla de privacidad **no** es editable aquí: lleva un enlace y tiene valor legal |

**Criterios de aceptación**
- [ ] CA-31.1 Cambiar el título de "Nombre" en el panel lo cambia en el formulario.
- [ ] CA-31.2 Si un título queda vacío, el sitio usa el texto original: nunca hay un campo sin título.

### RF-32 — Campos nuevos del formulario

Los tres son **opcionales**.

| ID | Requisito |
|---|---|
| RF-32.1 | Casilla **"Tengo fotos del espacio"** |
| RF-32.2 | Casilla **"No sé cuántos m² son, agendar una visita"**. Al marcarla, los campos de m² desaparecen y el estimado pasa a "A cotizar" |
| RF-32.3 | Campo de texto **"Ubicación del espacio"** |
| RF-32.4 | Los tres se guardan en la cotización, se ven en el panel y aparecen en el mensaje de WhatsApp (cada uno solo si se llenó o se marcó) |

**Criterios de aceptación**
- [ ] CA-32.1 Con "No sé cuántos m²" marcada, el formulario se envía sin metros y el backend lo acepta.
- [ ] CA-32.2 Sin esa casilla, los m² de cada área siguen siendo obligatorios.
- [ ] CA-32.3 Los títulos de estos tres campos también se editan en la tabla de RF-31.

### RF-33 — Iconos de contacto en el pie

Cambia RF-18.3 de specs-002 (los datos iban bajo el formulario).

| ID | Requisito |
|---|---|
| RF-33.1 | El pie de página muestra tres iconos con enlace: **WhatsApp**, **correo** e **Instagram** |
| RF-33.2 | Cada icono solo aparece si su dato está cargado en "Configuración general" |
| RF-33.3 | Se quita de la sección Contacto la fila de datos de contacto. Contacto queda con el título, la introducción y el formulario |

**Criterios de aceptación**
- [ ] CA-33.1 Cada icono tiene nombre para lectores de pantalla y mide al menos 44 × 44 px de área pulsable.
- [ ] CA-33.2 En móvil, el botón flotante de WhatsApp no tapa los iconos del pie.

---

## 3. Qué deja de aplicar de lo anterior

| Antes | Qué pasa |
|---|---|
| RF-06.7 (`specs/`): la capa de la tarjeta dice "Ver proyecto" | Sustituido por RF-22: muestra la descripción |
| Orden del inicio de specs-001 (P-8): Proyectos → Servicios → Proceso | Sustituido por RF-23: Proyectos → Proceso → Servicios |
| RF-08.9 (specs-001): el video es solo un respaldo del hero | Sustituido por RF-26: es una portada más |
| RF-17.2 (specs-002): un solo área por cotización | Sustituido por RF-27: varias, cada una con sus m² |
| RF-03.10 (`specs/`, modificado en la Fase 4): m² solo con la barra | Ampliado por RF-29: también escritos a mano |
| RF-18.3 (specs-002): datos de contacto bajo el formulario | Sustituido por RF-33: iconos en el pie |
| Mensaje de WhatsApp con emojis (`specs/design.md` §2.4) | Sustituido por RF-28 |
| Listas "Pasos del proceso" y "Servicios" en el menú del panel | Sustituidas por RF-25: dentro de su sección |

---

## 4. Decisiones confirmadas

Confirmadas por el desarrollador el 2026-10-09. Se numeran desde P-15 para no repetir las de los paquetes anteriores.

| # | Tema | Decisión |
|---|---|---|
| P-15 | Varias áreas | **m² por cada área**; el estimado es la suma |
| P-16 | Video en el hero | El video es **una portada más** de la rotación |
| P-17 | Texto sobre la portada | **La descripción completa** del proyecto |
| P-18 | Categoría no visible | Se oculta **solo la categoría** (inicio, filtro y formulario); sus proyectos siguen en "Todos" |
| P-19 | Tipografía | **Dos fuentes:** títulos y texto |
| P-20 | Precio oculto | Oculto **para el visitante**; RP Design lo sigue viendo en el panel |
| P-21 | Campos nuevos del formulario | **Todos opcionales**, incluida la ubicación |
| P-22 | Menú tras el cambio de orden | **No cambia** |

## 5. Más decisiones confirmadas

Propuestas por el agente y aceptadas por el desarrollador el 2026-10-09.

| # | Tema | Decisión |
|---|---|---|
| P-23 | Descripción más larga que la foto | **Scroll dentro de la capa**, sin recortar |
| P-24 | Posición del video en la rotación | **Primera portada** |
| P-25 | Botón "Cotizar" en celulares | **Siempre visible** |
| P-26 | Pasos y servicios en el panel | **Solo dentro de su sección**; desaparecen las entradas sueltas del menú |
| P-27 | Texto de la casilla de privacidad | **No editable** desde la tabla de campos |
| P-28 | Ciudad ("Caracas, Venezuela") | Deja de mostrarse en Contacto; el lema del pie ya la menciona |
| P-29 | Total cuando un área no tiene precio | **"A cotizar"** para todo el total |
| P-30 | Formatos y tamaño de las fuentes | `woff2`, `woff`, `ttf`, `otf`; **2 MB** |

---

## 6. Requisitos no funcionales

Siguen vigentes RNF-01 a RNF-11. Se añade:

| ID | Requisito |
|---|---|
| RNF-12 | Las fuentes cargadas por el cliente no bloquean el primer pintado: el texto se ve antes con la fuente original |
| RNF-13 | El formulario, ahora más largo, sigue siendo usable con teclado y lector de pantalla: cada casilla y cada campo de m² tiene su etiqueta |

## 7. Lo que sigue pendiente después de este paquete

- **Despliegue (Fase 5 de `specs/tasks.md`, tareas T-5.1 a T-5.9):** dominio, Cloudflare (Pages, R2, DNS), Railway y lista de comprobación de seguridad. **No se ha empezado.** Depende de que el cliente compre el dominio y de crear las cuentas.
- **Textos legales** (T-4.13): los entrega el cliente o su abogado. Bloquean la publicación.
- **Pregunta abierta:** si el cliente quiere secciones Nosotros y Testimonios.

## 8. Fuera de alcance de specs-003

- Subir las fotos del espacio desde el formulario (la casilla solo avisa de que existen; se piden por WhatsApp).
- Agendar la visita en un calendario (la casilla solo avisa de que se necesita).
- Mapa o autocompletado para la ubicación: es un campo de texto.
- Varios videos en el hero, o un video por proyecto.
- Fuentes distintas por sección, o más de dos fuentes.
- Agregar, quitar o reordenar los campos del formulario desde el panel.

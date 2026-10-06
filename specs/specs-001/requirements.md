# Requisitos — specs-001: cambios pedidos por el cliente

> **Qué** cambia respecto a lo ya construido y **cómo sabemos que está bien hecho**.
> Es un paquete de cambios sobre la base de `specs/`. Donde este documento contradice a `specs/`, **manda este**.

**Estado:** Aprobado (v1, 2026-10-06)
**Base:** `specs/requirements.md` v3 (RF-01 a RF-07), ya implementada salvo el despliegue.
**Reglas:** las mismas de `AGENTS.md`: mismo stack, mismos tokens de diseño, SDD, tests, accesibilidad y animaciones solo con CSS.

---

## 1. Resumen de los cambios

| # | Pedido del cliente | Requisito |
|---|---|---|
| 1 | El hero pasa a mostrar las portadas de los proyectos, que rotan si hay más de una. Se elimina la frase del título | RF-08 |
| 2 | El botón "Agenda una visita" pasa a decir "Agenda una reunión" | RF-08.8 |
| 3 | La sección Proyectos del inicio pasa a mostrar **categorías** (Comercial, Residencial, Corporativo); al elegir una se ven sus proyectos. Se mantiene "Ver todos los proyectos" | RF-09 |
| 3.1 | El campo categoría de cada proyecto se asocia a esas categorías | RF-09.2 |
| 3.2 | La dirección web del proyecto se genera sola | RF-10 |
| 4 | El WhatsApp de Contacto se muestra en formato internacional (`+58 412…`) | RF-11 |
| 5 | Botón flotante de WhatsApp abajo a la derecha, con el mensaje "Hola! quiero agendar una reunión" | RF-12 |

---

## 2. Requisitos funcionales

### RF-08 — Hero con portadas de proyectos

Reemplaza a la Portada actual (S2 de `specs/requirements.md`) y a los "destacados" de RF-01.1.

| ID | Requisito |
|---|---|
| RF-08.1 | Cada proyecto tiene en el panel la casilla **"Mostrar en el hero"** y un orden entre los que la tienen marcada |
| RF-08.2 | El hero muestra, a todo el ancho y sobre fondo oscuro, las portadas de los proyectos **publicados** que tienen la casilla marcada, en ese orden |
| RF-08.3 | Con **más de una** portada, rotan solas con un fundido suave y un zoom lento. Con **una sola**, queda fija |
| RF-08.4 | Sobre cada portada se ve el **nombre del proyecto y su categoría**, y lleva a la página de ese proyecto |
| RF-08.5 | Hay controles para pasar a la anterior y a la siguiente, indicadores de posición y un botón para **pausar** la rotación. También se pausa con el cursor encima o con el foco del teclado |
| RF-08.6 | El **título** de la Portada sigue siendo editable en el panel, pero queda **vacío**: se elimina "Transformamos tus espacios, del plano a la obra.". Si el cliente escribe uno nuevo, se muestra; vacío, no se muestra nada |
| RF-08.7 | Se mantienen el antetítulo, el párrafo y los dos botones de la Portada, sobre las portadas |
| RF-08.8 | El texto del botón principal pasa de "Agenda una visita" a **"Agenda una reunión"** (sigue editable en el panel) |
| RF-08.9 | Si **ningún** proyecto tiene la casilla marcada, el hero usa la imagen o el video de la Portada del panel, como hasta ahora, dentro del nuevo diseño. Si tampoco hay, queda el fondo oscuro con el texto |
| RF-08.10 | Se eliminan "Destacado" y "Orden entre destacados" de los proyectos, y con ellos el límite de 3 destacados. Los sustituye "Mostrar en el hero" |
| RF-08.11 | Como máximo **6** proyectos pueden estar en el hero a la vez; el panel lo impide con un mensaje claro |

**Criterios de aceptación**
- [ ] CA-08.1 Con 0, 1 y varios proyectos marcados, el hero no muestra huecos ni bloques rotos.
- [ ] CA-08.2 Con una sola portada no hay rotación, ni controles, ni indicadores.
- [ ] CA-08.3 Un proyecto en borrador no aparece en el hero aunque tenga la casilla marcada.
- [ ] CA-08.4 La rotación se detiene con el botón de pausa, con el cursor encima y con el foco del teclado.
- [ ] CA-08.5 Con "reducir movimiento" activo no hay rotación automática ni zoom; las portadas se cambian con los controles, sin transición.
- [ ] CA-08.6 Un lector de pantalla no anuncia cada cambio automático de portada.
- [ ] CA-08.7 Con el título vacío, la página conserva un único título principal (para accesibilidad y buscadores) aunque no se vea.
- [ ] CA-08.8 La primera portada se carga con prioridad; las demás, solo cuando hacen falta.
- [ ] CA-08.9 En una base de datos recién creada, el botón principal dice "Agenda una reunión" y el título está vacío.

### RF-09 — Categorías de proyectos

Cambia la sección Proyectos del inicio (S5) y la página `/proyectos`.

| ID | Requisito |
|---|---|
| RF-09.1 | Existe la lista **Categorías** en el panel: el cliente las agrega, edita y ordena arrastrando. Se crean tres al inicio: **Comercial, Residencial y Corporativo** |
| RF-09.2 | Cada proyecto pertenece a **una** categoría, elegida de esa lista. Reemplaza al campo de texto libre "categoría" |
| RF-09.3 | La sección Proyectos del inicio muestra una **tarjeta por categoría** en lugar de los proyectos destacados |
| RF-09.4 | Al elegir una categoría se abre `/proyectos` mostrando solo los proyectos de esa categoría. La dirección se puede copiar y compartir |
| RF-09.5 | En `/proyectos` hay un filtro con "Todos" y cada categoría, para cambiar sin volver al inicio |
| RF-09.6 | Se mantiene el botón **"Ver todos los proyectos"** |
| RF-09.7 | La imagen de la tarjeta de una categoría la **decide el cliente**: cada proyecto tiene la casilla **"Usar como portada de su categoría"**. Si ninguno la tiene marcada, se usa la portada del primer proyecto publicado de esa categoría |
| RF-09.8 | Solo un proyecto por categoría puede ser su portada: al marcar uno, se desmarca el anterior |
| RF-09.9 | Una categoría **sin proyectos publicados** no se muestra en el sitio |
| RF-09.10 | La etiqueta de categoría de las tarjetas de proyecto y de la página de detalle muestra el nombre de la categoría |
| RF-09.11 | Una categoría con proyectos no se puede eliminar |

**Criterios de aceptación**
- [ ] CA-09.1 Con una base de datos recién creada existen las tres categorías.
- [ ] CA-09.2 Si ninguna categoría tiene proyectos publicados, la sección Proyectos del inicio se oculta entera.
- [ ] CA-09.3 `/proyectos?categoria=residencial` muestra solo los proyectos de Residencial, y el botón "atrás" del navegador funciona.
- [ ] CA-09.4 Una categoría que no existe en la dirección muestra todos los proyectos, no un error.
- [ ] CA-09.5 Los borradores no cuentan para decidir si una categoría se muestra, ni pueden ser su portada visible.
- [ ] CA-09.6 Los proyectos que ya existían conservan su categoría si el texto coincide con una de las nuevas; si no, quedan sin categoría y el panel pide elegirla al editarlos.

### RF-10 — Dirección web automática de los proyectos

| ID | Requisito |
|---|---|
| RF-10.1 | La dirección web (slug) de un proyecto **no se escribe a mano**: se genera sola a partir del título al crearlo. En el panel se ve, pero no se edita |
| RF-10.2 | Si el título tiene **una sola palabra**, se completa con la palabra "proyecto" **al principio**: "Casa" → `proyecto-casa` |
| RF-10.3 | Si la dirección ya existe, se le agrega un número: `proyecto-casa-2` |
| RF-10.4 | La dirección **no cambia** al editar el título después, para no romper enlaces ya compartidos |
| RF-10.5 | La dirección de las categorías también se genera sola a partir de su nombre, sin la palabra "proyecto": "Residencial" → `residencial` |

**Criterios de aceptación**
- [ ] CA-10.1 En el formulario de proyecto del panel no hay un campo para escribir la dirección web.
- [ ] CA-10.2 "Remodelación de cocina" → `remodelacion-de-cocina`; "Casa" → `proyecto-casa`.
- [ ] CA-10.3 Los proyectos que ya existen conservan su dirección actual.

### RF-11 — WhatsApp en formato internacional

| ID | Requisito |
|---|---|
| RF-11.1 | El número de WhatsApp se muestra en el sitio en formato internacional: `+58 412 730 5964` |
| RF-11.2 | El formato se calcula a partir del número del panel. Se elimina el campo "WhatsApp como se muestra", para que no puedan quedar distintos |
| RF-11.3 | Un número de otro país se muestra como `+` seguido de sus dígitos, sin inventar agrupaciones |

**Criterios de aceptación**
- [ ] CA-11.1 En Contacto se lee "WhatsApp: +58 412 730 5964".
- [ ] CA-11.2 Al cambiar el número en el panel, el formato mostrado cambia solo.

### RF-12 — Botón flotante de WhatsApp

| ID | Requisito |
|---|---|
| RF-12.1 | En todas las páginas hay un botón con el **icono clásico de WhatsApp** (círculo verde con el logotipo blanco), fijo en la esquina **inferior derecha** |
| RF-12.2 | Al pulsarlo se abre WhatsApp hacia el número del panel con el mensaje ya escrito: **"Hola! quiero agendar una reunión"** |
| RF-12.3 | El mensaje es editable en el panel, y hay un interruptor para mostrar u ocultar el botón |
| RF-12.4 | El botón no tapa contenido importante ni queda encima del visor de imágenes |

**Criterios de aceptación**
- [ ] CA-12.1 El enlace abre `wa.me/<número>` con el mensaje del panel, en móvil y en escritorio.
- [ ] CA-12.2 El botón tiene nombre accesible ("Escribir por WhatsApp"), se alcanza con el teclado y mide al menos 48 × 48 px.
- [ ] CA-12.3 En móvil no tapa el botón "Enviar por WhatsApp" del formulario ni los enlaces del pie.
- [ ] CA-12.4 Con el interruptor apagado, o sin número de WhatsApp, el botón no aparece.

---

## 3. Qué deja de aplicar de `specs/`

| En `specs/requirements.md` | Qué pasa |
|---|---|
| RF-01.1, CA-01.1 y CA-01.2 (3 destacados en el inicio) | Sustituidos por RF-08 (hero) y RF-09 (categorías) |
| S2 Portada (foto a un lado del texto) | Sustituida por RF-08. La maqueta deja de ser la referencia **para el hero** |
| S5 Proyectos (3 tarjetas de proyectos) | Sustituida por RF-09 (tarjetas de categorías). Se conserva el estilo: fondo oscuro, mismas tarjetas |
| RF-06.2, RF-06.5 y RF-06.6 en la Portada (botones desde la derecha, video, zoom ligado al scroll) | En el hero los reemplaza la rotación de RF-08.3. El video y el zoom ligado al scroll quedan solo para el caso de RF-08.9 y para la portada del detalle de proyecto |
| "WhatsApp como se muestra" en la configuración (RF-04.5) | Eliminado por RF-11.2 |
| Dirección web editable del proyecto (`design.md` §2.3) | Sustituida por RF-10 |

Todo lo demás de `specs/` sigue vigente: calculadora, panel y roles, contenido editable, páginas legales, seguridad y animaciones del resto del sitio.

---

## 4. Decisiones confirmadas

Confirmadas por el desarrollador el 2026-10-06.

| # | Tema | Decisión |
|---|---|---|
| P-1 | Palabra "proyecto" en la dirección de una sola palabra | **Al principio:** `proyecto-casa` |
| P-2 | Máximo de portadas en el hero | **6** |
| P-3 | Aspecto del botón flotante | **El icono clásico de WhatsApp:** círculo verde con el logotipo blanco. Es la única pieza redonda además del logo del encabezado |
| P-4 | A dónde lleva "Agenda una reunión" del hero | **A la sección Contacto** |
| P-5 | Tiempo entre portadas | **6 segundos**, fijo en el código |
| P-6 | Título de la sección de categorías | **"Mis Proyectos"** (antes "Proyectos recientes"). Sigue editable en el panel |
| P-7 | Proyecto sin categoría | El panel **exige** elegir una al guardar. Los que queden sin categoría por la migración solo aparecen en "Todos" |

---

## 5. Requisitos no funcionales

Siguen vigentes RNF-01 a RNF-08 de `specs/requirements.md`. Se añade:

| ID | Requisito |
|---|---|
| RNF-09 | El hero no empeora el rendimiento: la primera portada es la única que se carga con prioridad, y Lighthouse Performance sigue ≥ 85 en móvil |
| RNF-10 | La rotación del hero cumple la pauta de contenido en movimiento: se puede pausar y respeta "reducir movimiento" |

## 6. Fuera de alcance de specs-001

- Varias categorías por proyecto.
- Subcategorías o etiquetas.
- Videos en el hero cuando hay portadas de proyectos marcadas.
- Estadísticas de clics del botón de WhatsApp.
- El despliegue (sigue siendo la última fase).

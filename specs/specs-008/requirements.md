# Requisitos — specs-008: sexta ronda de cambios del cliente

> **Qué** cambia respecto a lo ya construido y **cómo sabemos que está bien hecho**.
> Es un paquete de cambios sobre `specs/` y los paquetes anteriores. Donde este documento los contradice, **manda este**.

**Estado:** Aprobado (v1, 2026-10-13) — el desarrollador aprobó el plan y pidió desarrollarlo
**Reglas:** las mismas de `AGENTS.md`. Sin dependencias nuevas.

> ⚠️ El **despliegue definitivo** sigue pendiente (`specs/tasks.md`, Fase 5). La demo de `specs/specs-006/` recibe estos cambios al subirlos a GitHub.

---

## 1. Resumen de los cambios

| # | Pedido del cliente | Requisito |
|---|---|---|
| 1 | La sección "Un solo equipo para todo tu proyecto" muestra el **proceso** en tarjetas numeradas, no los servicios | RF-58 |
| 2 | El video del proceso se conserva, con una casilla para mostrarlo u ocultarlo | RF-59 |
| 3 | Una sección en negro con los **servicios**, arriba de Proyectos: portada con animación y "Cotizar", sin números | RF-60 |
| 4 | "Tipo de remodelación" es un texto libre | RF-61 |
| 5 | Ya no hay áreas por categoría: un solo campo de m², opcional, junto a la ubicación | RF-62 |
| 6 | Sin estimado de precio | RF-63 |
| 7 | Las animaciones de entrada se repiten cada vez que el elemento vuelve a la pantalla | RF-64 |

**Descartado:** cambiar el fondo de la sección Proyectos. Se queda en negro, como está.

**Orden del inicio:** Hero → Servicios (negro) → Proyectos (negro) → Proceso en tarjetas (claro) → Contacto. (Ajustado por el desarrollador el 2026-10-13: Servicios va arriba de Proyectos.)

---

## 2. Requisitos funcionales

### RF-58 — El proceso en tarjetas numeradas

1. La sección Proceso se muestra sobre fondo claro, con su título, su introducción y una cuadrícula de **tarjetas numeradas** (01, 02, 03…): número, título del paso y descripción. Es el aspecto de la referencia que entregó el desarrollador (el que tenían los servicios antes de specs-004).
2. Reemplaza a la presentación anterior del proceso (lista con letras A, B, C).
3. El título "Un solo equipo para todo tu proyecto" y su introducción pasan a ser los de esta sección. Se editan en el panel, en "Proceso".
4. Los pasos se siguen editando y ordenando dentro de "Proceso" en el panel. El número sale del orden.

**Criterios de aceptación**
- [ ] CA-58.1 Con 3, 4 o más pasos la cuadrícula se ve bien a 360, 768, 1280 y 1920 px.
- [ ] CA-58.2 Sin pasos visibles, la sección no se muestra.

### RF-59 — Video del proceso con casilla

1. "Proceso" en el panel tiene una casilla nueva, **"Mostrar el video"**.
2. El video se muestra en la sección solo si la casilla está marcada **y** hay un video cargado. Si no, la sección se ve solo con las tarjetas.
3. La casilla empieza marcada: quien ya tenía un video cargado lo sigue viendo.

**Criterios de aceptación**
- [ ] CA-59.1 Desmarcar la casilla oculta el video sin borrarlo; marcarla lo vuelve a mostrar.

### RF-60 — Servicios en sección negra, sin números

1. Los servicios van en su propia sección, sobre fondo negro, **justo después del hero y antes de Proyectos**.
2. Cada tarjeta muestra la portada del servicio con su animación, la descripción y el botón "Cotizar" (como en specs-004 y specs-005), **sin número**.
3. El título de la sección es editable en el panel y empieza como **"Servicios"**; la introducción empieza vacía.

**Criterios de aceptación**
- [ ] CA-60.1 Ninguna tarjeta de servicio muestra número.
- [ ] CA-60.2 Las capas siguen funcionando con cursor, con teclado y en táctil.

### RF-61 — Tipo de remodelación como texto libre

1. "Tipo de remodelación" pasa de desplegable a un **campo de texto** obligatorio, con el ejemplo *"cocina, patio, baño, casa, quinta, etc."*
2. El título y el ejemplo siguen siendo editables en "Campos del formulario".
3. Las categorías dejan de usarse en el formulario. Siguen clasificando los proyectos y filtrando `/proyectos`.

### RF-62 — Metros cuadrados en un solo campo

1. Desaparecen las casillas de áreas y sus campos.
2. Junto a "Ubicación del espacio" hay un campo **"Metros cuadrados"**, **opcional** y **numérico**: solo deja escribir cifras, coma y punto, y acepta un número mayor que 0. Su texto de ejemplo es **"10 m²"** (editable en el panel).
3. La casilla "No sé cuántos m² son, agendar una visita" se mantiene. Marcada, el campo de m² se desactiva y lo escrito no se envía.

**Criterios de aceptación**
- [ ] CA-62.1 El formulario se envía sin m² y sin marcar la casilla.
- [ ] CA-62.2 Un valor que no es un número, o que es 0 o negativo, muestra el error en ese campo.

### RF-63 — Sin estimado de precio

1. El formulario no muestra ningún precio, y el mensaje de WhatsApp tampoco.
2. El mensaje incluye: nombre, correo, teléfono, tipo de remodelación, ubicación, m² (si los dio), "quiero agendar una visita" (si lo marcó), "tengo fotos" (si lo marcó) y el mensaje.
3. En el panel dejan de mostrarse lo que ya no tiene efecto: "Áreas y precios", la casilla del estimado, la nota de precio y el máximo de m². Sus datos no se borran.
4. Las **cotizaciones anteriores** se conservan tal cual, con sus áreas y montos, y se siguen viendo en el panel.

**Criterios de aceptación**
- [ ] CA-63.1 Una cotización nueva queda en el panel con su tipo, ubicación y m².
- [ ] CA-63.2 Una cotización anterior se abre en el panel y muestra sus áreas y su estimado.
- [ ] CA-63.3 El backend rechaza una cotización sin tipo de remodelación o sin ubicación.

**Campos obligatorios:** nombre, teléfono, correo, tipo de remodelación, ubicación y la aceptación de privacidad.

### RF-64 — Las entradas se repiten

1. Las animaciones de entrada (títulos, textos, botones y tarjetas) se ejecutan **cada vez** que el elemento entra en la pantalla, no solo la primera: al salir de la vista vuelve a su estado inicial y, al regresar, se anima de nuevo.
2. Aplica al bajar y al subir por la página, en todas las secciones.
3. Con "reducir movimiento" nada cambia: todo se ve desde el principio, sin animación.
4. Al llegar al final de la página no queda nada oculto.

**Criterios de aceptación**
- [ ] CA-64.1 Al bajar hasta Proceso, subir y volver a bajar, las tarjetas numeradas entran de nuevo.
- [ ] CA-64.2 Ningún elemento se queda invisible mientras está a la vista.

---

## 3. Qué deja de aplicar de lo anterior

| Antes | Qué pasa |
|---|---|
| RF-03 (`specs/`) y RF-27 a RF-30 (specs-003): áreas, m² por área, estimado y su interruptor | Sustituidos por RF-61 a RF-63 |
| RF-17 (specs-002) y RF-42 (specs-005): tipo de remodelación = categorías | Sustituido por RF-61 |
| RF-06 (`specs/`): "cada animación de entrada ocurre una sola vez" | Sustituido por RF-64: se repite en cada entrada |
| RF-23 (specs-003): Proceso con letras; RF-35 y RF-36 (specs-004): números en las tarjetas de servicio | Sustituidos por RF-58 y RF-60 |
| "Un solo equipo para todo tu proyecto" como título de Servicios | Pasa a Proceso (RF-58.3) |

---

## 4. Decisiones confirmadas

| # | Tema | Decisión |
|---|---|---|
| P-55 | Estimado de precio | Se quita |
| P-56 | Sección Proceso anterior | Se reemplaza por las tarjetas numeradas; el video se conserva con una casilla |
| P-57 | Título de la sección negra | Editable; empieza como "Servicios" |
| P-58 | Fondo de Proyectos | Se queda en negro |
| P-59 | Campo de m² | Numérico simple, sin barra deslizante |
| P-60 | Lo que ya no se usa en el panel | Se retira de la vista sin borrar los datos |

---

## 5. Fuera de alcance

- Borrar de la base de datos las áreas, los precios o las cotizaciones anteriores.
- Cambios en el hero, el pie, `/proyectos` o el detalle de proyecto.

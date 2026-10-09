# Requisitos — specs-002: segunda ronda de cambios del cliente

> **Qué** cambia respecto a lo ya construido y **cómo sabemos que está bien hecho**.
> Es un paquete de cambios sobre `specs/` y `specs/specs-001/`. Donde este documento los contradice, **manda este**.

**Estado:** Implementado y cerrado (2026-10-08)

> ⚠️ **Dos puntos quedaron sustituidos por `specs/specs-003/requirements.md`:** RF-17.2 (un solo área por cotización) → varias áreas, cada una con sus m² (RF-27); y RF-18.3 (datos de contacto bajo el formulario) → iconos en el pie (RF-33). El resto de este paquete sigue vigente.
**Base:** `specs/` (RF-01 a RF-07) y `specs/specs-001/` (RF-08 a RF-12), ya implementadas.
**Reglas:** las mismas de `AGENTS.md`: mismo stack, mismos tokens de diseño, SDD, tests, accesibilidad y animaciones solo con CSS.

> ⚠️ **El despliegue sigue pendiente.** Es la última fase del proyecto (`specs/tasks.md`, Fase 5) y empieza al cerrar este paquete. Ver §7.

---

## 1. Resumen de los cambios

| # | Pedido del cliente | Requisito |
|---|---|---|
| 1 | El menú superior es siempre un botón que despliega las opciones debajo del logo | RF-13 |
| 1.1 | El encabezado no se muestra al bajar por la página | RF-13.5 |
| 2 | Poder mostrar u ocultar desde el panel los botones del hero | RF-14 |
| 3 | Controles de las portadas del hero (anterior, pausa, siguiente) más discretos | RF-15 |
| 4 | Eliminar el cintillo de servicios en movimiento | RF-16 |
| 5 | En el formulario, el área a remodelar depende del tipo de remodelación (la categoría), todo configurable en el panel | RF-17 |
| 5.1 | El formulario va debajo del título y ocupa todo el ancho | RF-18.1 |
| 6 | Los datos de contacto van debajo del formulario, uno al lado del otro | RF-18.3 |

El nombre de la sección Proyectos ya es editable en el panel ("Proyectos (encabezado)"): no requiere cambios.

---

## 2. Requisitos funcionales

### RF-13 — Menú desplegable y encabezado que se oculta

Cambia el encabezado (S1 de `specs/requirements.md`).

| ID | Requisito |
|---|---|
| RF-13.1 | En **todos los tamaños de pantalla**, las opciones del menú (Servicios, Proyectos, Proceso) están detrás de un botón desplegable. Ya no se muestran en línea en escritorio |
| RF-13.2 | El **botón del menú va a la izquierda del logo**, en la misma fila. Al pulsarlo, las opciones se despliegan debajo del encabezado |
| RF-13.3 | El botón **"Cotiza tu proyecto" no cambia**: sigue visible en el encabezado en escritorio y dentro del menú en móvil, como hoy |
| RF-13.4 | El menú se cierra al elegir una opción, con la tecla `Esc` y al pulsar fuera de él |
| RF-13.5 | El encabezado **se oculta al bajar** por la página y **reaparece al subir**. Arriba del todo está siempre visible |
| RF-13.6 | El encabezado no se oculta mientras el menú está desplegado ni mientras el foco del teclado está dentro de él |

**Criterios de aceptación**
- [ ] CA-13.1 A 1280 px y a 360 px, las opciones del menú no se ven hasta pulsar el botón.
- [ ] CA-13.2 El botón del menú indica si está abierto o cerrado a un lector de pantalla, y se maneja con el teclado.
- [ ] CA-13.3 Al bajar, el encabezado desaparece; al subir un poco, vuelve. No tapa el título de la sección al ir a un ancla.
- [ ] CA-13.4 Con "reducir movimiento" activo, el encabezado aparece y desaparece sin animación.
- [ ] CA-13.5 Navegando con el teclado, al llegar con `Tab` a un elemento del encabezado, este se muestra.

### RF-14 — Botones del hero configurables

| ID | Requisito |
|---|---|
| RF-14.1 | En "Portada" del panel hay dos interruptores: **mostrar el botón principal** ("Agenda una reunión") y **mostrar el botón secundario** ("Ver proyectos"). Los dos vienen activados |
| RF-14.2 | Un botón desactivado no se muestra en el hero. Con los dos desactivados, no queda un hueco |
| RF-14.3 | Se mantiene la regla actual: aunque esté activado, un botón no se muestra si la sección a la que lleva está oculta |

**Criterios de aceptación**
- [ ] CA-14.1 Con cada combinación (los dos, uno, ninguno) el hero se ve bien y sin espacio vacío.
- [ ] CA-14.2 El cambio se ve en el sitio al recargar, sin redeploy.

### RF-15 — Controles discretos en el hero

Cambia RF-08.5 de specs-001. Validado con la skill `ui-ux-pro-max`, cuya guía para contenido que rota solo es: debe conservar anterior, siguiente y pausa, y detenerse con el cursor, el foco y "reducir movimiento". Por eso los controles **se hacen discretos, no se quitan**.

| ID | Requisito |
|---|---|
| RF-15.1 | Desaparecen los tres botones con recuadro. Los controles pasan a ser una sola línea fina, abajo a la derecha del hero |
| RF-15.2 | Los **indicadores** (una barra por portada) son el control principal: se pulsan para ir a una portada, y la barra de la portada activa **se va llenando** mientras dura, a modo de progreso |
| RF-15.3 | **Anterior** y **siguiente** son dos flechas pequeñas sin recuadro, a los lados de los indicadores, atenuadas; se aclaran al pasar el cursor o al enfocarlas |
| RF-15.4 | **Pausa** es un icono pequeño sin recuadro, junto a los indicadores. Mientras la rotación está detenida (por la pausa, el cursor o el foco), la barra activa se muestra llena y quieta; al reanudar, vuelve a empezar junto con el tiempo de la portada |
| RF-15.5 | Aunque se vean pequeños, todos los controles conservan un área de pulsación cómoda para el dedo |

**Criterios de aceptación**
- [ ] CA-15.1 Los controles siguen funcionando con mouse, dedo y teclado, y tienen nombre para lectores de pantalla.
- [ ] CA-15.2 Cada control mide al menos 44 × 44 px de área pulsable, aunque el dibujo sea más pequeño.
- [ ] CA-15.3 Con una sola portada no hay controles, como hasta ahora.
- [ ] CA-15.4 Con "reducir movimiento", la barra activa se muestra llena, sin animación.

### RF-16 — Eliminar el cintillo de especialidades

Elimina S3 de `specs/requirements.md` y RF-06.4.

| ID | Requisito |
|---|---|
| RF-16.1 | El cintillo en movimiento deja de mostrarse en el inicio |
| RF-16.2 | La lista **"Especialidades" se conserva en el panel**, con un aviso de que ya no se muestra en el sitio, por si se quiere recuperar más adelante |

**Criterios de aceptación**
- [ ] CA-16.1 En el inicio, después del hero viene directamente la sección Proyectos (orden de specs-001: Portada → Proyectos → Servicios → Proceso → Contacto).
- [ ] CA-16.2 El panel explica, en la propia lista, que las especialidades ya no se muestran.

### RF-17 — Área a remodelar según el tipo de remodelación

Cambia RF-03.2 y RF-03.3 de `specs/requirements.md`.

| ID | Requisito |
|---|---|
| RF-17.1 | El formulario tiene un campo nuevo y obligatorio, **"Tipo de remodelación"**, cuyas opciones son las **categorías** de proyectos (Residencial, Corporativo, Comercial…) |
| RF-17.2 | El campo "Área a remodelar" muestra **solo las áreas del tipo elegido**. Hasta que no se elige un tipo, está deshabilitado |
| RF-17.3 | En el panel, cada área se asigna a una categoría. Todo es configurable: categorías, áreas, a qué categoría pertenece cada área y su precio |
| RF-17.4 | Un área **sin categoría** aparece en **todos** los tipos. Así funciona la opción "Otro" |
| RF-17.5 | Áreas iniciales: **Residencial** → Baño, Cocina, Sala, Patio, Piscina (las actuales). **Corporativo** → Oficina, Sala de reuniones. **Comercial** → Showroom. Las nuevas se crean sin precio |
| RF-17.6 | Al cambiar de tipo, el área elegida se borra y hay que elegirla de nuevo |
| RF-17.7 | La cotización guarda el tipo elegido, y el mensaje de WhatsApp lo incluye |
| RF-17.8 | Una categoría sin ninguna área activa (ni propia ni común) no aparece en el formulario |
| RF-17.9 | Una categoría que tiene áreas no se puede eliminar sin reasignarlas antes |

**Criterios de aceptación**
- [ ] CA-17.1 Con Residencial se ofrecen Baño, Cocina, Sala, Patio, Piscina y Otro; con Corporativo, Oficina, Sala de reuniones y Otro; con Comercial, Showroom y Otro.
- [ ] CA-17.2 Crear un área en el panel y asignarla a una categoría la hace aparecer en el formulario al recargar.
- [ ] CA-17.3 El backend rechaza una cotización cuya área no pertenece al tipo enviado.
- [ ] CA-17.4 El precio estimado sigue calculándose igual: m² × precio del área; "A cotizar" si no tiene precio o es "Otro".
- [ ] CA-17.5 Las cotizaciones anteriores se conservan, aunque no tengan tipo.
- [ ] CA-17.6 El mensaje de WhatsApp incluye el tipo de remodelación.

### RF-18 — Nueva distribución de la sección Contacto

Cambia S7 de `specs/requirements.md` y RF-03.11.

| ID | Requisito |
|---|---|
| RF-18.1 | La sección pasa a una sola columna: **título e introducción arriba**, **formulario debajo** ocupando todo el ancho y el alto que necesite |
| RF-18.2 | En pantallas anchas, los campos del formulario se reparten en varias columnas para aprovechar el ancho. En móvil siguen uno debajo del otro |
| RF-18.3 | Los **datos de contacto** (WhatsApp, correo, Instagram, ciudad) van **debajo del formulario**, uno al lado del otro. En móvil, si no caben, pasan a la línea siguiente |
| RF-18.4 | Orden de los campos: Nombre, Teléfono, Correo, Tipo de remodelación, Área a remodelar, (Especifica el área), Metros cuadrados, Estimado, Mensaje, aceptación de privacidad y botón |

**Criterios de aceptación**
- [ ] CA-18.1 A 1280 px el formulario ocupa todo el ancho del contenido y los datos de contacto están en una fila debajo.
- [ ] CA-18.2 A 360 px no hay scroll horizontal y todo sigue siendo usable con el dedo.
- [ ] CA-18.3 El orden al recorrer el formulario con `Tab` coincide con el orden visual.

---

## 3. Qué deja de aplicar de lo anterior

| Antes | Qué pasa |
|---|---|
| S1 Encabezado: menú en línea en escritorio y encabezado siempre fijo (`specs/`) | Sustituido por RF-13 |
| RF-08.5 de specs-001: tres botones con recuadro en el hero | Sustituido por RF-15 |
| S3 Franja de especialidades y RF-06.4 (`specs/`) | Eliminados por RF-16. La lista queda en el panel sin uso |
| RF-03.2: lista única de áreas (`specs/`) | Sustituido por RF-17: áreas por tipo |
| S7 Contacto en dos columnas y RF-03.11 (`specs/`) | Sustituidos por RF-18 |
| El botón flotante de WhatsApp se oculta en Contacto (specs-001) | Se mantiene, y se revisa con la nueva distribución |

---

## 4. Decisiones confirmadas

Confirmadas por el desarrollador el 2026-10-07.

| # | Tema | Decisión |
|---|---|---|
| Q-1 | Encabezado al hacer scroll | Se oculta al bajar y **vuelve al subir** |
| Q-2 | Botón "Cotiza tu proyecto" | **No se toca:** queda donde está hoy |
| Q-3 | Lista "Especialidades" | **Solo se quita del sitio**; se conserva en el panel |
| Q-4 | Áreas iniciales de Corporativo y Comercial | Oficina y Sala de reuniones; Showroom |

## 5. Más decisiones confirmadas

Confirmadas por el desarrollador el 2026-10-07. Se numeran desde P-10 para no repetir las de specs-001 (P-1 a P-9).

| # | Tema | Decisión |
|---|---|---|
| P-10 | Opción "Otro" | **Una sola**, sin categoría, que aparece en todos los tipos |
| P-11 | Tipos del formulario | Son las **mismas categorías** de los proyectos. En el formulario el campo se llama "Tipo de remodelación", pero sus opciones salen de la lista de categorías |
| P-12 | Reparto de los campos en escritorio | A criterio del agente: **tres columnas** (Nombre · Teléfono · Correo / Tipo · Área · Especifica / Metros en 2 columnas · Estimado / Mensaje a todo el ancho) |
| P-13 | Barra de progreso en el indicador activo del hero | **Sí** |
| P-14 | Menú desplegable | El **botón del menú va a la izquierda del logo**, y las opciones se despliegan debajo. Decidido el 2026-10-08 tras probar dos versiones: a la derecha junto a "Cotiza tu proyecto", y debajo del logo |

---

## 6. Requisitos no funcionales

Siguen vigentes RNF-01 a RNF-10. Se añade:

| ID | Requisito |
|---|---|
| RNF-11 | Ocultar y mostrar el encabezado no provoca saltos en el contenido ni afecta el rendimiento al hacer scroll |

## 7. Lo que sigue pendiente después de este paquete

- **Despliegue (Fase 5 de `specs/tasks.md`, tareas T-5.1 a T-5.9):** dominio, Cloudflare (Pages, R2, DNS), Railway y lista de comprobación de seguridad. **No se ha empezado.** Depende de que el cliente compre el dominio y de crear las cuentas.
- **Textos legales** (T-4.13): los entrega el cliente o su abogado. Bloquean la publicación.
- **Pregunta abierta:** si el cliente quiere secciones Nosotros y Testimonios.

## 8. Fuera de alcance de specs-002

- Deslizar con el dedo para cambiar de portada en el hero.
- Precios distintos para una misma área según la categoría (cada área tiene un solo precio).
- Un área que pertenezca a dos categorías a la vez (o es de una, o es común a todas).
- Cambios en la calculadora más allá del campo nuevo y la distribución.

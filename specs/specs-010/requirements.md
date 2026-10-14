# Requisitos — specs-010: botón "Volver" en la página de proyectos

> **Qué** se construye. Octavo paquete de cambios del cliente.

**Estado:** Implementado y cerrado (2026-10-14)

**Reglas:** las mismas de `AGENTS.md`. Este paquete solo describe lo que cambia; lo demás sigue como en `specs/` y en los paquetes anteriores.

---

## 1. Resumen

| # | Pedido | Requisito |
|---|---|---|
| 1 | En `/proyectos` (la página con los filtros) no hay una forma clara de volver. Arriba del título "Proyectos Realizados" debe verse una flecha blanca y la palabra "Volver" | RF-67 |

---

## 2. Requisitos funcionales

### RF-67 — "Volver" en `/proyectos`

- Arriba del título de la página se muestra **"← Volver"**, en blanco.
- Lleva al **inicio, a la sección Proyectos** (`/#proyectos`), que es desde donde se llega con el botón "Ver proyectos".
- Es un enlace normal (no el "atrás" del navegador). Cambiar de filtro cambia la dirección, y con "atrás" la persona iría pasando por cada filtro que tocó en vez de salir de la página.
- Se ve igual con cualquier filtro activo, en escritorio y en celular.
- Al pasar el cursor, la flecha se mueve un poco hacia la izquierda (solo `transform`), como la flecha del botón "Ver proyectos". Con "reducir movimiento" no se mueve.
- Área cómoda para tocar con el dedo (mínimo 44 px de alto) y usable con el teclado (foco visible).

**Criterios de aceptación**
- [ ] CA-67.1 En `/proyectos` y en `/proyectos?categoria=…` aparece "← Volver" en blanco, arriba del título.
- [ ] CA-67.2 Al pulsarlo se llega al inicio, con la sección Proyectos a la vista.
- [ ] CA-67.3 Se alcanza con Tab y se activa con Enter.

---

## 3. Lo que no cambia

- El título, los filtros y la cuadrícula de `/proyectos`.
- El enlace "← Todos los proyectos" del detalle de un proyecto (ver P-68).

---

## 4. Decisiones propuestas (revisar)

| # | Tema | Propuesta | Motivo |
|---|---|---|---|
| P-67 | A dónde lleva | Al inicio, en la sección Proyectos (`/#proyectos`) | Es el lugar desde donde se entra; "atrás" del navegador recorrería los filtros |
| P-68 | El "← Todos los proyectos" del detalle | Se queda como está (gris) | No lo pediste; si quieres que también sea blanco, es un cambio de una línea |
| P-69 | Texto | Fijo, "Volver", no editable en el panel | Es un texto de navegación, como "Saltar al contenido"; no es contenido del cliente |

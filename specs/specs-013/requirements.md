# Requisitos — specs-013: dificultar la descarga casual de imágenes

> **Qué** cambia en el sitio público.
> Este paquete solo describe lo que cambia; lo demás sigue como en `specs/` y en los paquetes anteriores.

**Estado:** Implementado y verificado localmente (2026-11-13)

---

## 1. Resumen

| # | Pedido | Requisito |
|---|---|---|
| 1 | Dificultar que se guarden imágenes desde el menú del clic derecho | RF-74 |
| 2 | Evitar que las imágenes se arrastren directamente desde la página | RF-74 |

---

## 2. Requisitos funcionales

### RF-74 — Dificultar la descarga casual de imágenes

- En el sitio público, al hacer clic derecho sobre una imagen no se abre el menú contextual del navegador.
- Las imágenes del sitio no se pueden arrastrar directamente desde la página.
- La medida aplica a las imágenes visibles del sitio, incluyendo portada, proyectos, servicios, galería y visor de imágenes.
- La medida no bloquea el menú contextual sobre textos, enlaces, controles o campos del formulario, ni cambia el comportamiento de videos.
- Las imágenes siguen siendo visibles y sus enlaces, controles, navegación y textos alternativos continúan funcionando.
- No se agregan dependencias.
- Esta medida solo añade fricción: no impide obtener las imágenes desde las herramientas del navegador o la red, ni tomar capturas de pantalla.

**Criterios de aceptación**

- [x] CA-74.1 El clic derecho sobre una imagen del hero, una tarjeta de proyecto, una tarjeta de servicio, la galería o el visor no muestra el menú contextual del navegador.
- [x] CA-74.2 Una imagen no se puede arrastrar fuera de su elemento en las mismas secciones.
- [x] CA-74.3 El menú contextual sigue disponible sobre texto, enlaces, controles y campos del formulario.
- [x] CA-74.4 La galería, el visor, los enlaces y la navegación siguen funcionando con mouse y teclado.
- [x] CA-74.5 Los videos mantienen sus controles y no se altera su interacción.
- [x] CA-74.6 Se confirma en la prueba manual que las imágenes todavía se pueden obtener desde las herramientas del navegador; no se presenta la medida como protección absoluta.

---

## 3. Lo que no cambia

- Las imágenes que el cliente sube, sus marcas de agua y la forma en que el backend las procesa y sirve.
- Los permisos, endpoints y almacenamiento del backend.
- La calidad, tamaño y resolución de las imágenes.
- Los textos, estilos y contenido del sitio.

---

## 4. Alcance y limitaciones

Este cambio es una disuasión de frontend para descargas casuales. No protege los archivos frente a personas que inspeccionen las solicitudes de red, usen herramientas de desarrollo o capturen la pantalla. Las imágenes visibles en un sitio público no se pueden volver imposibles de copiar solo con código del navegador.

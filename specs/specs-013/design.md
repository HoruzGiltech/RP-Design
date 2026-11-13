# Diseño — specs-013: dificultar la descarga casual de imágenes

> **Cómo** se construye. Solo lo que cambia.

## 1. Frontend

- Agregar `onContextMenu` y `onDragStart` al contenedor común `.layout` en `SiteFrame`, dentro de `frontend/src/components/layout/Layout.jsx`.
- En cada evento, comprobar que el elemento que lo originó tiene `tagName === 'IMG'`. Solo entonces llamar a `preventDefault()`.
- La delegación desde el contenedor común cubre las imágenes de todas las rutas públicas, incluidas las que se renderizan después de cargar contenido o abrir el visor. No requiere cambiar cada componente de imagen.
- No interceptar eventos sobre texto, enlaces, botones, campos del formulario ni elementos `<video>`.
- No se cambia el CSS, el backend, los recursos de imagen ni la resolución.

## 2. Pruebas

- En las pruebas unitarias de los manejadores, enviar eventos `contextmenu` y `dragstart` desde una imagen y comprobar que se cancelan.
- Enviar los mismos eventos desde texto, controles y videos y comprobar que no se cancelan.
- Comprobar manualmente una imagen del hero, una tarjeta, la galería y el visor, además de verificar que controles de video y navegación siguen funcionando.

## 3. Decisiones y límites

| Tema | Decisión |
|---|---|
| Cobertura | Delegar los eventos desde `.layout` para proteger de forma consistente las imágenes de todas las páginas públicas |
| Alcance | Cancelar menú contextual y arrastre solo cuando el origen del evento sea una imagen |
| Backend y archivos | Sin cambios: los recursos siguen siendo públicos y se pueden obtener desde las herramientas del navegador o la red |
| Accesibilidad | No bloquear menús contextuales ni interacciones de elementos que no sean imágenes |

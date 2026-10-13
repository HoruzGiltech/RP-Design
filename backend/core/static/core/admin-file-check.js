/*
  Revisa cada archivo del panel en el momento de elegirlo (specs-007, RF-56).

  Por qué existe: si una foto pasa del tamaño máximo, el servidor rechaza el
  formulario y el navegador pierde TODOS los archivos elegidos (por seguridad,
  un campo de archivo no se puede volver a rellenar). Avisando aquí, antes de
  enviar, solo se descarta el archivo que no sirve.

  Las reglas de cada campo vienen en su atributo data-upload-rules, que pone
  el servidor (core/admin_mixins.py): {"jpg": 5, "png": 5, "mp4": 50}
  significa "estos formatos, con este máximo en MB cada uno".

  El servidor vuelve a validar todo al guardar: esto es solo un aviso temprano.
*/
(function () {
  "use strict";

  var BYTES_PER_MB = 1024 * 1024;
  var MESSAGE_CLASS = "file-check-message";

  /** "Foto Sala.JPG" -> "jpg" */
  function getExtension(fileName) {
    var parts = fileName.split(".");
    return parts.length > 1 ? parts.pop().toLowerCase() : "";
  }

  /** 7549747 -> "7,2" (con coma decimal, como se escribe aquí) */
  function formatMegabytes(bytes) {
    return (bytes / BYTES_PER_MB).toFixed(1).replace(".", ",");
  }

  /** Devuelve el motivo por el que el archivo no sirve, o null si está bien. */
  function findProblem(file, rules) {
    var maxMegabytes = rules[getExtension(file.name)];

    if (maxMegabytes === undefined) {
      return "Formato no permitido. Usa: " + Object.keys(rules).join(", ") + ".";
    }
    if (file.size > maxMegabytes * BYTES_PER_MB) {
      return (
        "Este archivo pesa " + formatMegabytes(file.size) + " MB. " +
        "El máximo es " + maxMegabytes + " MB. Elige uno más liviano."
      );
    }
    return null;
  }

  function removeMessage(input) {
    var previous = input.parentNode.querySelector("." + MESSAGE_CLASS);
    if (previous) previous.remove();
  }

  function showMessage(input, text) {
    // "errorlist" es la clase que usa el panel para sus propios errores
    var list = document.createElement("ul");
    list.className = "errorlist " + MESSAGE_CLASS;
    // role="alert": un lector de pantalla lo anuncia en cuanto aparece
    list.setAttribute("role", "alert");
    var item = document.createElement("li");
    item.textContent = text;
    list.appendChild(item);
    input.parentNode.insertBefore(list, input);
  }

  function checkInput(input) {
    removeMessage(input);

    var file = input.files && input.files[0];
    if (!file) return;

    var problem = findProblem(file, JSON.parse(input.dataset.uploadRules));
    if (!problem) return;

    // Solo se vacía este campo: los demás archivos elegidos no se tocan
    input.value = "";
    showMessage(input, file.name + ": " + problem);
  }

  // Se escucha en todo el documento y no en cada campo: así también funciona
  // con las filas de la galería que se agregan después con "Agregar otro".
  document.addEventListener("change", function (event) {
    var input = event.target;
    if (input.type === "file" && input.dataset.uploadRules) {
      checkInput(input);
    }
  });
})();

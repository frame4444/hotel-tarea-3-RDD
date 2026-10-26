// Envía el formulario del filtro al cambiar la opción (sin JavaScript sigue el botón).
document.querySelectorAll("select[data-auto]").forEach(function (s) {
  s.addEventListener("change", function () { s.form.submit(); });
});

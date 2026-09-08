document.addEventListener("DOMContentLoaded", function () {
  var toggle = document.getElementById("nav-toggle");
  var nav = document.getElementById("primary-nav");
  if (!toggle || !nav) return;

  toggle.addEventListener("click", function () {
    var isOpen = nav.classList.toggle("is-open");
    toggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
  });
});

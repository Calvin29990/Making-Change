/* Making Change — progressive enhancement only.
   The page is fully usable without JavaScript: every control is inside a GET
   form and "Recompute" submits it. This file adds live labels and debounce
   auto-submit so moving a slider updates the URL (and the result) without
   requiring a click. */
(function () {
  "use strict";

  var forms = Array.prototype.slice.call(document.querySelectorAll("form.controls"));
  if (!forms.length) return;

  var timer = null;

  function debounceSubmit(form) {
    if (timer) clearTimeout(timer);
    timer = setTimeout(function () {
      // requestSubmit keeps the GET semantics and the noscript fallback intact
      if (typeof form.requestSubmit === "function") form.requestSubmit();
      else form.submit();
    }, 420);
  }

  forms.forEach(function (form) {
    form.querySelectorAll('input[type="range"]').forEach(function (input) {
      var out = form.querySelector("[id='" + input.id + "-out']") ||
                form.querySelector("#" + input.id + "-out");
      var unit = input.name === "coverage" || input.name === "shock" ? " %" : "";

      function paint() {
        if (!out) return;
        var v = input.name === "cost" || input.name === "threshold"
          ? parseFloat(input.value).toFixed(2)
          : Math.round(parseFloat(input.value));
        if (input.name === "cost" && !unit) unit = " %";
        if (input.name === "threshold") unit = "x";
        out.textContent = v + (input.name === "cost" ? " %" : unit);
        var pct = (input.value - input.min) / (input.max - input.min) * 100;
        input.style.background =
          "linear-gradient(to right, var(--market) 0%, var(--market) " + pct +
          "%, var(--line) " + pct + "%, var(--line) 100%)";
      }

      paint();
      input.addEventListener("input", paint);
      input.addEventListener("change", function () { debounceSubmit(form); });
    });

    // a numeric hedged-rate change also refreshes the result on blur
    form.querySelectorAll('input[type="number"]').forEach(function (input) {
      input.addEventListener("change", function () { debounceSubmit(form); });
    });
  });

  // highlight the active tab/step in the address bar without reloading anything
  if (window.location.hash) {
    var target = document.querySelector(window.location.hash);
    if (target) target.scrollIntoView({ behavior: "smooth", block: "start" });
  }
})();

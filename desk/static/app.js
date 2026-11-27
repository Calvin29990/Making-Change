/* Making Change — progressive enhancement.
   The page works without this file: every control sits in a GET form.
   Here we only add live label painting, a debounced auto-submit so moving a
   slider updates the URL, tab highlighting on scroll, and copy-to-clipboard on
   the URL bar — the reproduction guarantee of the whole desk. */
(function () {
  "use strict";

  function copyButton(btn) {
    btn.addEventListener("click", function () {
      var el = document.querySelector(btn.getAttribute("data-copy"));
      if (!el) return;
      var text = (el.value !== undefined ? el.value : el.textContent) || "";
      var flash = function () {
        var old = btn.textContent;
        btn.textContent = "copié ✓";
        setTimeout(function () { btn.textContent = old; }, 1400);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(flash, flash);
      } else {
        try { el.select(); document.execCommand("copy"); } catch (e) {}
        flash();
      }
    });
  }
  document.querySelectorAll("[data-copy]").forEach(copyButton);

  var timer = null;
  function submitLater(form) {
    clearTimeout(timer);
    timer = setTimeout(function () {
      if (typeof form.requestSubmit === "function") form.requestSubmit();
      else form.submit();
    }, 450);
  }

  function paint(input, out) {
    var name = input.name;
    var raw = parseFloat(input.value);
    var text;
    var suffix = "";
    if (name === "coverage" || name === "shock" || name === "cost") {
      text = Math.round(raw);
      suffix = " %";
      if (name === "cost") text = raw.toFixed(2);
    } else if (name === "threshold") {
      text = raw.toFixed(2);
      suffix = "x";
    } else {
      text = String(raw);
    }
    if (out) out.textContent = text + suffix;
    var min = parseFloat(input.min || 0);
    var max = parseFloat(input.max || 100);
    var pct = max > min ? ((raw - min) / (max - min)) * 100 : 0;
    input.style.background =
      "linear-gradient(to right, var(--mint) 0%, var(--mint) " + pct +
      "%, var(--line-strong) " + pct + "%, var(--line-strong) 100%)";
  }

  Array.prototype.slice.call(document.querySelectorAll("form")).forEach(function (form) {
    Array.prototype.slice.call(form.querySelectorAll('input[type="range"]')).forEach(function (input) {
      var out = document.getElementById(input.id + "-out");
      paint(input, out);
      input.addEventListener("input", function () { paint(input, out); });
      input.addEventListener("change", function () { submitLater(form); });
    });
    Array.prototype.slice.call(form.querySelectorAll('input[type="number"]')).forEach(function (input) {
      if (input.name === "principal") return; // no submit on every keystroke
      input.addEventListener("change", function () { submitLater(form); });
    });
    Array.prototype.slice.call(form.querySelectorAll("select")).forEach(function (sel) {
      sel.addEventListener("change", function () { form.submit(); });
    });
  });

  // tab highlight on scroll
  var tabs = Array.prototype.slice.call(document.querySelectorAll("nav.tabs a[href^='#']"));
  var sections = tabs.map(function (a) {
    return document.querySelector(a.getAttribute("href"));
  }).filter(Boolean);
  if ("IntersectionObserver" in window && sections.length) {
    var obs = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        tabs.forEach(function (a) {
          a.classList.toggle("on", a.getAttribute("href") === "#" + e.target.id);
        });
      });
    }, { rootMargin: "-15% 0px -75% 0px" });
    sections.forEach(function (s) { obs.observe(s); });
  }
})();

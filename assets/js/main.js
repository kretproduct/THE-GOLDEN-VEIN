(function () {
  "use strict";

  var D = window.TGV || { contact: {}, proofs: [], cases: [] };
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var fine = window.matchMedia("(hover: hover) and (pointer: fine)").matches;

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }
  var ICON = {
    img: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3"><path d="M3 5h18v14H3z"/><path d="m3 16 5-5 4 4 3-3 6 6"/><circle cx="15.5" cy="9" r="1.5"/></svg>',
    arrow: '<svg viewBox="0 0 30 12" fill="none" stroke="currentColor" stroke-width="1.4"><path d="M0 6h28M23 1l5 5-5 5"/></svg>'
  };

  /* ---------- Контакты и год ---------- */
  var contacts = (D.contacts || (D.contact ? [D.contact] : [])).filter(function (c) { return c && c.url && c.url !== "#"; });
  var TG = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M21.9 4.3 18.7 19c-.2 1-.9 1.3-1.7.8l-4.7-3.5-2.3 2.2c-.3.3-.5.5-1 .5l.3-4.8L18 6.4c.4-.3-.1-.5-.6-.2L6.700 13l-4.600-1.400c-1-.3-1-1 .2-1.500l18-6.900c.8-.3 1.600.2 1.600 1.100Z"/></svg>';
  function contactLink(c, cls) {
    var a = el("a", cls);
    a.href = c.url; a.target = "_blank"; a.rel = "noopener";
    a.innerHTML = TG; a.appendChild(el("span", "", c.label || c.url));
    return a;
  }
  if (contacts.length === 1) {
    $$("[data-contact]").forEach(function (a) { a.href = contacts[0].url; a.target = "_blank"; a.rel = "noopener"; });
  } else if (contacts.length > 1) {
    var cm = el("dialog"); cm.id = "contact-modal"; cm.setAttribute("aria-label", "Связаться с нами");
    var xb = el("button", "x", "×"); xb.type = "button"; xb.setAttribute("aria-label", "Закрыть");
    var sheet = el("div", "sheet"), cb = el("div", "body");
    cb.appendChild(el("span", "eyebrow", "Telegram"));
    cb.appendChild(el("div", "ttl", "Кому написать"));
    contacts.forEach(function (c) { cb.appendChild(contactLink(c, "btn")); });
    sheet.appendChild(cb); cm.appendChild(xb); cm.appendChild(sheet);
    document.body.appendChild(cm);
    $$("[data-contact]").forEach(function (a) {
      var box = a.parentNode;
      if (box.classList.contains("cta")) {
        // большой блок внизу страницы: показываем все контакты сразу
        contacts.forEach(function (c) { box.insertBefore(contactLink(c, "btn"), a); });
        box.removeChild(a);
        return;
      }
      a.href = contacts[0].url; a.setAttribute("role", "button"); a.setAttribute("aria-haspopup", "dialog");
      a.addEventListener("click", function (e) {
        if (!cm.showModal) return;
        e.preventDefault();
        cm.showModal();
      });
    });
  }
  $$("[data-year]").forEach(function (n) { n.textContent = new Date().getFullYear(); });

  /* ---------- Шапка и меню ---------- */
  var header = $(".header"), burger = $(".burger"), nav = $(".nav");
  function setMenu(open) {
    nav.classList.toggle("open", open);
    burger.setAttribute("aria-expanded", String(open));
    document.body.style.overflow = open ? "hidden" : "";
  }
  if (burger && nav) {
    burger.addEventListener("click", function () { setMenu(!nav.classList.contains("open")); });
    nav.addEventListener("click", function (e) { if (e.target.closest("a")) setMenu(false); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") setMenu(false); });
  }

  /* ---------- Скролл: шапка, жила прогресса, линия пути ---------- */
  var veinFill = $(".scroll-vein .fill"), pathBox = $(".path"), ticking = false;
  function onScroll() {
    ticking = false;
    var y = window.scrollY, max = document.documentElement.scrollHeight - window.innerHeight;
    if (header) header.classList.toggle("scrolled", y > 24);
    if (veinFill) veinFill.style.strokeDashoffset = String(1 - (max > 0 ? Math.min(1, y / max) : 1));
    if (pathBox) {
      var r = pathBox.getBoundingClientRect();
      var p = (window.innerHeight * 0.62 - r.top) / r.height;
      pathBox.style.setProperty("--p", Math.max(0, Math.min(1, p)).toFixed(3));
    }
  }
  function reqScroll() { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } }
  window.addEventListener("scroll", reqScroll, { passive: true });
  window.addEventListener("resize", reqScroll);
  onScroll();

  /* ---------- Появление при скролле ---------- */
  var io = "IntersectionObserver" in window ? new IntersectionObserver(function (entries) {
    entries.forEach(function (en) {
      if (en.isIntersecting) { en.target.classList.add("in-view"); io.unobserve(en.target); }
    });
  }, { threshold: 0.12, rootMargin: "0px 0px -6% 0px" }) : null;
  function watch(nodes) {
    nodes.forEach(function (n) { if (io) io.observe(n); else n.classList.add("in-view"); });
  }

  /* ---------- Наклон карточек и блик ---------- */
  function tilt(card) {
    if (!fine || reduced) return;
    card.addEventListener("pointermove", function (e) {
      var r = card.getBoundingClientRect(), x = (e.clientX - r.left) / r.width, y = (e.clientY - r.top) / r.height;
      card.style.setProperty("--px", (x * 100).toFixed(1) + "%");
      card.style.setProperty("--py", (y * 100).toFixed(1) + "%");
      card.style.setProperty("--ry", ((x - 0.5) * 5).toFixed(2) + "deg");
      card.style.setProperty("--rx", ((0.5 - y) * 5).toFixed(2) + "deg");
    });
    card.addEventListener("pointerleave", function () {
      card.style.setProperty("--rx", "0deg"); card.style.setProperty("--ry", "0deg");
    });
  }

  /* ---------- Пруфы ---------- */
  var proofsBox = $("#proofs");
  if (proofsBox) {
    var shots = [];
    (D.proofs || []).forEach(function (p, i) {
      var has = !!p.src, card = el(has ? "button" : "div", "proof card reveal");
      card.style.setProperty("--d", (i % 3) * 0.08 + "s");
      var inner = el("div", "in");
      if (has) {
        card.type = "button";
        var img = new Image();
        img.src = p.src; img.alt = p.title || "Пруф " + (i + 1); img.loading = "lazy"; img.decoding = "async";
        img.onerror = function () { card.remove(); var k = shots.indexOf(p); if (k > -1) shots.splice(k, 1); };
        inner.appendChild(img);
        shots.push(p);
        card.setAttribute("aria-label", "Открыть: " + img.alt);
        card.addEventListener("click", function () { openLightbox(shots.indexOf(p)); });
      } else {
        var ph = el("div", "ph");
        ph.style.aspectRatio = ["4/5", "1/1", "4/3"][i % 3];
        ph.innerHTML = ICON.img;
        ph.appendChild(el("span", "", "Место для пруфа №" + (i + 1)));
        inner.appendChild(ph);
      }
      if (p.title || p.note) {
        var cap = el("div", "cap");
        if (p.title) cap.appendChild(el("b", "", p.title));
        if (p.note) cap.appendChild(document.createTextNode(p.note));
        inner.appendChild(cap);
      }
      card.appendChild(inner);
      proofsBox.appendChild(card);
    });

    var lb = $("#lightbox"), lbImg = $("#lightbox img"), lbCap = $("#lightbox figcaption"), lbCount = $(".lb-count"), cur = 0;
    var show = function (i) {
      cur = (i + shots.length) % shots.length;
      var p = shots[cur];
      lbImg.src = p.src; lbImg.alt = p.title || "";
      lbCap.textContent = "";
      if (p.title) lbCap.appendChild(el("b", "", p.title));
      if (p.note) lbCap.appendChild(document.createTextNode(p.note));
      lbCount.textContent = (cur + 1) + " / " + shots.length;
      $$(".lb-nav", lb).forEach(function (b) { b.hidden = shots.length < 2; });
    };
    var openLightbox = function (i) { show(i); lb.showModal(); };
    $(".lb-prev", lb).addEventListener("click", function () { show(cur - 1); });
    $(".lb-next", lb).addEventListener("click", function () { show(cur + 1); });
    lb.addEventListener("keydown", function (e) {
      if (e.key === "ArrowLeft") show(cur - 1);
      if (e.key === "ArrowRight") show(cur + 1);
    });
    var sx = null;
    lb.addEventListener("touchstart", function (e) { sx = e.touches[0].clientX; }, { passive: true });
    lb.addEventListener("touchend", function (e) {
      if (sx == null) return;
      var dx = e.changedTouches[0].clientX - sx; sx = null;
      if (Math.abs(dx) > 50) show(cur + (dx < 0 ? 1 : -1));
    });
  }

  /* ---------- Кейсы ---------- */
  var casesBox = $("#cases");
  if (casesBox) {
    var modal = $("#case-modal"), body = $("#case-modal .body");
    var avatar = function (c, i) {
      var a = el("div", "avatar");
      if (c.photo) { var im = new Image(); im.src = c.photo; im.alt = ""; im.loading = "lazy"; a.appendChild(im); }
      else a.textContent = c.name ? c.name.trim().charAt(0).toUpperCase() : String(i + 1);
      return a;
    };
    var delta = function (c) {
      var d = el("div", "delta"), a = el("div"), b = el("div", "to"), arrow = el("span");
      a.appendChild(el("small", "", "Было")); a.appendChild(el("b", "", c.before || "Точка А"));
      arrow.innerHTML = ICON.arrow;
      b.appendChild(el("small", "", c.period ? "Стало · " + c.period : "Стало")); b.appendChild(el("b", "", c.after || "Точка Б"));
      d.appendChild(a); d.appendChild(arrow); d.appendChild(b);
      return d;
    };
    var head = function (c, i) {
      var top = el("div", "top"), t = el("div");
      t.appendChild(el("div", "name", c.name || "Ученик №" + (i + 1)));
      if (c.role || !c.name) t.appendChild(el("div", "role", c.role || "Здесь будет описание"));
      top.appendChild(avatar(c, i)); top.appendChild(t);
      return top;
    };
    (D.cases || []).forEach(function (c, i) {
      var full = !!(c.story || (c.shots && c.shots.length));
      var card = el(full ? "button" : "div", "case card reveal");
      card.style.setProperty("--d", (i % 3) * 0.08 + "s");
      var inner = el("div", "in");
      inner.appendChild(head(c, i));
      inner.appendChild(delta(c));
      if (c.summary) inner.appendChild(el("p", "sum", c.summary));
      if (c.quote) inner.appendChild(el("blockquote", "", "«" + c.quote + "»"));
      if (!c.summary && !c.quote) inner.appendChild(el("blockquote", "", "Здесь появится история ученика — пришлите текст кейса."));
      if (full) {
        card.type = "button";
        inner.appendChild(el("span", "more", "Читать кейс"));
        card.addEventListener("click", function () {
          body.textContent = "";
          body.appendChild(head(c, i));
          body.appendChild(delta(c));
          if (c.summary) body.appendChild(el("p", "sum", c.summary));
          if (c.quote) body.appendChild(el("blockquote", "", "«" + c.quote + "»"));
          if (c.story) body.appendChild(el("div", "story", c.story));
          (c.shots || []).forEach(function (s) {
            var im = new Image(); im.src = s; im.alt = "Скриншот к кейсу"; im.className = "shot"; im.loading = "lazy";
            body.appendChild(im);
          });
          modal.showModal(); body.scrollTop = 0;
        });
      }
      card.appendChild(inner);
      casesBox.appendChild(card);
    });
  }

  /* ---------- Диалоги: закрытие ---------- */
  $$("dialog").forEach(function (d) {
    d.addEventListener("click", function (e) { if (e.target === d || e.target.closest(".x")) d.close(); });
  });

  $$(".card").forEach(tilt);
  watch($$(".reveal, .step"));

  /* ---------- Свет «фонаря» за курсором ---------- */
  var torch = $(".torch");
  if (torch && fine) {
    var tx = 0, ty = 0, tq = false;
    window.addEventListener("pointermove", function (e) {
      tx = e.clientX; ty = e.clientY;
      if (!tq) {
        tq = true;
        requestAnimationFrame(function () {
          tq = false;
          torch.style.setProperty("--mx", tx + "px"); torch.style.setProperty("--my", ty + "px");
          torch.classList.add("on");
        });
      }
    }, { passive: true });
    document.addEventListener("mouseleave", function () { torch.classList.remove("on"); });
  }

  /* ---------- Золотая пыль ---------- */
  var cv = $("#dust");
  if (cv && !reduced && cv.getContext) {
    var ctx = cv.getContext("2d"), W, H, dpr, parts = [], raf = 0;
    var size = function () {
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      W = window.innerWidth; H = window.innerHeight;
      cv.width = W * dpr; cv.height = H * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      var n = Math.round(Math.min(70, W * H / 26000));
      parts = [];
      for (var i = 0; i < n; i++) parts.push({
        x: Math.random() * W, y: Math.random() * H, r: Math.random() * 1.5 + 0.3,
        vy: -(Math.random() * 0.22 + 0.05), vx: (Math.random() - 0.5) * 0.12,
        ph: Math.random() * 6.28, sp: Math.random() * 0.02 + 0.006
      });
    };
    var frame = function () {
      ctx.clearRect(0, 0, W, H);
      for (var i = 0; i < parts.length; i++) {
        var p = parts[i];
        p.x += p.vx; p.y += p.vy; p.ph += p.sp;
        if (p.y < -5) { p.y = H + 5; p.x = Math.random() * W; }
        if (p.x < -5) p.x = W + 5; else if (p.x > W + 5) p.x = -5;
        ctx.globalAlpha = 0.15 + 0.55 * (0.5 + 0.5 * Math.sin(p.ph));
        ctx.fillStyle = "#ffd978";
        ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, 6.2832); ctx.fill();
      }
      raf = requestAnimationFrame(frame);
    };
    var rt;
    window.addEventListener("resize", function () { clearTimeout(rt); rt = setTimeout(size, 200); });
    document.addEventListener("visibilitychange", function () {
      cancelAnimationFrame(raf);
      if (!document.hidden) raf = requestAnimationFrame(frame);
    });
    size(); raf = requestAnimationFrame(frame);
  }

  /* ---------- Переход между страницами ---------- */
  var veil = $(".veil");
  if (veil && !reduced) {
    document.addEventListener("click", function (e) {
      var a = e.target.closest("a[href]");
      if (!a || e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
      if (a.target === "_blank" || a.hasAttribute("download")) return;
      var url;
      try { url = new URL(a.href, location.href); } catch (err) { return; }
      if (url.origin !== location.origin || !/\.html?$|\/$/.test(url.pathname)) return;
      if (url.pathname === location.pathname) return;
      e.preventDefault();
      veil.classList.add("leaving");
      setTimeout(function () { location.href = url.href; }, 400);
    });
    window.addEventListener("pageshow", function (e) { if (e.persisted) veil.classList.remove("leaving"); });
  }
})();

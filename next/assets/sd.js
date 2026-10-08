/* Scroll-driven motion for browsers without native support (Safari 18 and older, Firefox), plus the safe fallback.

   The head script picks one of three modes and puts it on <html>:
     sd-native  the browser runs scroll-driven animation itself; nothing here drives the drawing.
     sd-poly    the drawing is driven from here: every CSS animation that carries a scroll range (--sd-range, see
                the generated block in styles.css) is paused and its time is set from the scroll position, using the
                same cover/contain range maths as the browser. Keyframes, easing and values all stay in CSS.
     sd-static  no drawing: the plain page (video, statement, three sections, closing line, footer).

   ?mode=static forces the static page. ?debug=1 shows which mode is active. */
(function () {
  var root = document.documentElement, cl = root.classList;
  var params = location.search;

  function mode() { return cl.contains('sd-native') ? 'native' : cl.contains('sd-poly') ? 'poly' : 'static'; }
  var wantPoly = cl.contains('sd-want-poly');
  function toStatic(why) {
    cl.remove('sd-native'); cl.remove('sd-poly'); cl.add('sd-static'); wantPoly = false;
    root.setAttribute('data-sd-why', why || '');
    if (window.__sdStop) window.__sdStop();
    paintDebug();
  }

  /* ---- debug label (?debug=1) ---- */
  var dbg;
  function paintDebug() {
    if (!/[?&]debug=1/.test(params)) return;
    if (!dbg) {
      dbg = document.createElement('div');
      dbg.style.cssText = 'position:fixed;left:8px;bottom:8px;z-index:99999;font:12px/1.4 monospace;background:#111;color:#fff;padding:6px 8px;border-radius:4px;opacity:.9;pointer-events:none;white-space:pre';
      document.body.appendChild(dbg);
    }
    dbg.textContent = 'mode: ' + mode() + (root.getAttribute('data-sd-why') ? ' (' + root.getAttribute('data-sd-why') + ')' : '') +
      (window.__sdCount != null ? '\ndriven animations: ' + window.__sdCount : '');
  }

  /* ---- header colour and the film dissolving (modes without native scroll timelines) ---- */
  var ticking = false;
  function clamp01(x) { return x < 0 ? 0 : x > 1 ? 1 : x; }
  function wide() { return window.matchMedia('(min-width: 901px)').matches; }
  function chrome() {
    ticking = false;
    if (cl.contains('sd-native')) return;
    var vh = window.innerHeight, p = (window.pageYOffset || 0) / vh;
    cl.toggle('hdr-dark', wide() ? p > 0.59 : true);
    var st = document.querySelector('.statement'), film = document.querySelector('.film');
    if (cl.contains('sd-poly') && wide()) {
      if (st) st.style.opacity = String(1 - clamp01((p - 0.30) / 0.25));
      if (film) film.style.opacity = String(1 - clamp01((p - 0.40) / 0.50));
    } else {
      if (st) st.style.opacity = '';
      if (film) film.style.opacity = '';
    }
  }
  function onScroll() { if (!ticking) { ticking = true; requestAnimationFrame(function () { chrome(); drive(); }); } }

  /* ---- the driver for sd-poly ---- */
  var items = [], flow = null, lastS = -1;
  function parseRanges(str) {
    // "cover 0% contain 70.4%, cover 0% cover 4%"  ->  [[a,b],[c,d]]
    return str.split(',').map(function (part) {
      var m = []; part.replace(/(cover|contain)\s+(-?\d*\.?\d+)%/g, function (_, n, v) { m.push([n, parseFloat(v)]); return ''; });
      return m.length === 2 ? m : null;
    });
  }
  function build() {
    items = []; lastS = -1;
    flow = document.querySelector('.flow');
    if (!flow) return;
    var V = window.innerHeight, r = flow.getBoundingClientRect();
    var top = r.top + (window.pageYOffset || 0), H = r.height;
    var a = top, b = top + H - V;
    var g = { cover: [top - V, top + H], contain: [Math.min(a, b), Math.max(a, b)] };
    var all = flow.querySelectorAll('*'), n = 0;
    for (var i = 0; i < all.length; i++) {
      var el = all[i], cs = getComputedStyle(el), rng = cs.getPropertyValue('--sd-range').trim();
      if (!rng) continue;
      var names = cs.animationName.split(',').map(function (s) { return s.trim(); });
      var ranges = parseRanges(rng);
      var anims = el.getAnimations({ subtree: false });
      for (var k = 0; k < anims.length; k++) {
        var an = anims[k], idx = an.animationName === undefined ? k : names.indexOf(an.animationName);
        if (idx < 0) continue;
        var rg = ranges[idx % ranges.length];
        if (!rg) continue;
        var s0 = g[rg[0][0]][0] + (g[rg[0][0]][1] - g[rg[0][0]][0]) * rg[0][1] / 100;
        var s1 = g[rg[1][0]][0] + (g[rg[1][0]][1] - g[rg[1][0]][0]) * rg[1][1] / 100;
        if (s1 === s0) continue;
        an.pause();
        items.push({ a: an, s0: s0, s1: s1, last: -1 });
        n++;
      }
    }
    window.__sdCount = n;
  }
  function drive() {
    if (!cl.contains('sd-poly')) return;
    var s = window.pageYOffset || 0;
    if (s === lastS) return; lastS = s;
    for (var i = 0; i < items.length; i++) {
      var it = items[i], p = clamp01((s - it.s0) / (it.s1 - it.s0));
      if (Math.abs(p - it.last) > 0.0002 || it.last < 0) { it.a.currentTime = p * 1000; it.last = p; }
    }
  }
  window.__sdStop = function () { items = []; };

  function start() {
    // captions follow the film in every mode
    if (!cl.contains('sd-native')) { chrome(); window.addEventListener('scroll', onScroll, { passive: true }); }
    window.addEventListener('resize', function () { clearTimeout(start.t); start.t = setTimeout(function () { if (cl.contains('sd-poly')) { build(); drive(); } chrome(); }, 150); });

    if (wantPoly) {
      try {
        cl.remove('sd-static'); cl.add('sd-poly');
        build();
        if (!items.length) { toStatic('no scroll animations were found'); }
        else { drive(); }
      } catch (e) { toStatic('driver error: ' + e.message); }
      // geometry changes once fonts and the video have settled
      window.addEventListener('load', function () { if (cl.contains('sd-poly')) { build(); lastS = -1; drive(); chrome(); paintDebug(); } });
    } else if (cl.contains('sd-native')) {
      // make sure the browser really runs the timeline, not just parses it
      try {
        var p = document.createElement('div');
        p.style.cssText = 'position:fixed;left:-9px;top:0;width:1px;height:1px;opacity:.01;pointer-events:none;animation:sd-probe 1s linear both;animation-timeline:scroll(root)';
        document.body.appendChild(p);
        var an = p.getAnimations();
        var ok = an.length > 0 && (!window.ScrollTimeline || an[0].timeline instanceof window.ScrollTimeline);
        document.body.removeChild(p);
        if (!ok) toStatic('native scroll timeline did not start');
      } catch (e) { toStatic('probe error: ' + e.message); }
    }
    paintDebug();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
})();

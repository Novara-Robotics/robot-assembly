# robot-assembly

The Novara Robotics site at novararobotics.ai. Novara is a robotic contract assembler: a customer sends a product and its
CAD, and Novara plans the build, runs the robot cells and delivers finished units. The site is static, hosted on GitHub
Pages (deploys from `main`), all paths relative. There is no bundler: the HTML and CSS are served as written, but two small Python scripts generate parts
of them (see **Build steps** below), so **edit, then run the scripts, then commit**.

The `.com` site (Deri) is a separate repo, `Novara-Robotics.github.io`, and never mentions this one.

## Files

- `index.html`, `styles.css` - the page
- `privacy.html`, `terms.html`, `404.html` - legal pages and the 404, same shell
- `assets/` - hero video and poster, `mark.svg` logo, favicons and app icons, self-hosted Geist, `sd.js` (generated,
  see below), and the link-preview image `og-share-contract-2.jpg` (1200x630, a frame from the 1080p factory render with the logo only,
  no text, so it does not go stale when the wording changes; link apps cache it, so use a new filename if you replace it)
- `scripts/` - build scripts (below)
- `replay/` - kept on purpose: an interactive three.js replay of the recorded MuJoCo factory run, reachable at
  `/replay/` but not linked from the page and marked `noindex`. The viewer code also lives in the
  `robot-assembly-demo` repo (`web/factory/`); the big data files (`scene.glb`, `traj.bin.gz`, `traj.json`) are
  generated there by `sim/scripts/18_export_web.py` from `trajectory.npz`, and are committed here as a backup.
- `CNAME` - the custom domain for GitHub Pages. Keep it.

## The page

A looping factory video with the headline "Contract assembly, done by robots." on it. As you scroll the film dissolves
and a line drawing takes over: parts drift in, three stages (Plan, Adapt, Assemble) step through it with a short
description each, the lines fan out and the parts meet under two arms, then the finished product leaves and the closing
line appears. The page has no numeric claims.

On phones (portrait, up to 900px wide) the same drawing is laid out as a single column, capped at 34rem and centred.
Landscape phones and tablets use the desktop layout. `viewport-fit=cover` and `env(safe-area-inset-*)` keep content
clear of notches.

## Build steps

Run from the repo root after editing `index.html`, `styles.css` or `scripts/sd.js`. All scripts are idempotent.

1. `python3 scripts/gen-mobile.py` - builds the phone version of the line: the phone SVG in `index.html` and the
   generated block between `MOBILE-START` / `MOBILE-END` in `styles.css`. Edit its constants (lanes, merge point `MY`,
   height `Hm`) to change the phone layout. The phone hero, header and footer rules live in a separate block that the
   script does not touch. It calls `scripts/smooth-keyframes.py`, which resamples the sampled motion keyframes 4x
   with monotone cubic interpolation so speed does not step at the joints.
2. `python3 scripts/compat-build.py .` - the compatibility build (below). It patches `index.html` and `styles.css` in
   place and copies `scripts/sd.js` to `assets/sd.js`.

Local preview:

    python3 -m http.server 4173

## Motion

Motion is CSS: the line draws itself and the parts advance along `offset-path` as you scroll (scroll-driven
animation, `animation-timeline: view()` per stage), plus independent loops (arm pick cycles, die cutting, drift).
Both fallbacks show the line whole, so nothing depends on animation: `prefers-reduced-motion: reduce`, and
browsers without scroll timelines (below).

On phones and desktop the lines and the parts/arms are two stacked SVG layers with a fixed CSS gradient between them
(`.trail-fade` on phones, `.trail-fade-d` on desktop) that fades the lines near the top. It replaced an SVG mask, which
forced a full repaint every scroll frame.

Two traps worth remembering:

- The `animation` shorthand resets `animation-range`. Use longhands or every animation collapses onto one shared range.
- `pathLength="1"` normalises a path to one unit, so a `9 9` dash pattern renders solid.

## Compatibility build

Scroll-driven animation is native in Chrome/Edge 115+ and Safari 26+. Safari 18 and older, and Firefox, do not have
it. A head script (added by `compat-build.py`) picks one of three modes from the browser alone and puts it on `<html>`
as a class. There are no URL overrides.

- `sd-native`: the browser's own animation, unchanged (the original `@supports` blocks are untouched).
- `sd-poly`: `assets/sd.js` pauses every CSS animation that carries a scroll range and sets its time from the scroll
  position, with the same cover/contain maths as the browser (checked against Chrome to four decimals). Keyframes and
  easing stay in CSS. It starts as the static page and switches on only after the driver has really built itself. If the first attempt finds nothing (for example on a cold load before the styles have settled) it tries again after the page
  has loaded, and 1 s and 3 s later, before settling for the plain page; the same retries guard the native-mode check.
- `sd-static`: the plain page (video, statement, three sections, closing line, footer). Used for reduced motion, no
  script, or a failed or blocked driver.

`scripts/sd.js` is the source of `assets/sd.js`; never edit the copy in `assets/`.

Animations that only change a custom property (`calm`, `calm-m`, `walk-on`, `pace-on`) are not run by the CSS engine
in `sd-poly`. `sd.js` sets `--amp`, `--walk` and `--pace` inline from the scroll position instead, because Firefox does
not re-read `var()` inside other animations' keyframes when such a property is animated.

## Design

- Theme: light, locked. Radius: all-sharp (0).
- Palette (see the custom properties at the top of `styles.css`): `--accent #a85a2c` sampled from the robot arms in
  the hero render, plus `--s2 #2d5f78`, `--s3 #8d7230` and `--s4 #4f7f48` for the parts. All under 80% saturation,
  text contrast at least 4.4:1.
- Type: Geist variable, self-hosted. No third-party requests on any page.

## Known limitations

Accepted on purpose; everything else was tested and works.

- **iPhone Chrome, landscape after rotating from portrait:** the layout turns desktop with side margins and the footer
  stays stacked. Chrome on iOS keeps a stale page width after rotation (likely cause, not verified). Safari is fine.
- **iPad landscape:** the Plan / Adapt / Assemble caption can collide with the header's "n" and "Contact us".
- **Mobile Safari:** the top robot part is sometimes visible before scrolling.
- **Plain fallback page:** reduced motion, no JavaScript or a failed driver show the video, statement, three sections
  and footer, without the drawing.
- **Firefox and Safari 18 or older** run the scripted copy of the animation (`sd-poly`), not the native one. It matched
  Chrome to within a few pixels in tests (a caption mid-fade was further off) and looked right on real devices.
- **Tested on:** Chrome (Ubuntu, Mac, iPhone portrait), Firefox (Ubuntu), Safari 18.6 (Mac), iPhone Safari (iOS 26),
  iPad Safari. Not tested: Android, Edge, older iOS, other Safari versions. Safari cannot be run in the dev environment,
  so Safari behaviour has only been checked by hand.
- **Edits need the build:** after changing `index.html`, `styles.css` or `scripts/sd.js`, run the two build steps above.
  Skipping them lets Firefox and Safari 18 drift from Chrome without any error.
- **`/replay/`:** reachable but not linked, 37 MB, `noindex`.
- **`noindex` is on** in the pages, so search engines do not list the site. When it comes off, add `robots.txt` and a
  sitemap.
- **No analytics (parked on purpose).** There is no visit counting yet, and on this backup site it would also break the
  "no third-party requests" claim above. Decision: free only and low priority. Options if it is picked up: Cloudflare
  Web Analytics (free, cookie-less, basic counts, probably no booking-click goal) or self-hosted Umami (free, more work).
  Paid tools such as Plausible or Fathom were ruled out for now. Adding any of them also needs one line in the Privacy
  Policy and one script tag in each page's head.

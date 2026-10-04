# robot-assembly

One-page site for Novara Robotics. Static (GitHub Pages, deploy from `main`), all paths
relative, no build step, **no JavaScript**.

- `index.html`, `styles.css` - the page
- `privacy.html`, `terms.html` - legal pages, same shell
- `assets/` - hero video, `mark.svg` logo, favicons, self-hosted Geist
- `scripts/gen-scene.py` - generates the diagram SVGs; paste its output into `index.html`
- `replay/` - three.js replay of the recorded MuJoCo run. In the repo, not linked.

## The page

1. **Hero** - the statement, with the parts drifting around it; they fade as you scroll on
2. **Play** - the parts, still drawings, drift around the centre of the page
3. **Plan** - they arrive on the right and get straightened
4. **Tooling** - the line crosses left; a die per lane cuts itself to that part's profile
5. **Assemble** - the lanes fan wide, then the parts travel in and meet under two arms
6. **Leave** - the line stops and the product keeps going

Every stage is full width so the line can cross the page between steps. The words alternate
left, right, left, right, at the height where the line has already settled on the far side.
Seams measure 0px and no text block is within 100px of the drawing.

## Motion

Two systems, no scroll listeners anywhere.

- **Scroll-driven** (`view-timeline` per stage): each stage inks its own lines in as you
  reach it.
- **Scroll-driven**: the line draws itself, and the parts advance along `offset-path` with
  the scroll (each gets a slice of its stage timeline), so they stop when you stop.
- **Independent loops**: lateral drift on each part, arm pick cycles, the die cutting its
  profile, and the merge that converges, stalls, then commits.

Two traps worth remembering:

- The `animation` shorthand resets `animation-range`. Use longhands or every animation
  collapses onto one shared range.
- `pathLength="1"` normalises a path to one unit, so a `9 9` dash pattern renders solid.
  The dashed re-route branch therefore fades in rather than drawing.

Both fallbacks show the line whole, so nothing depends on animation:
`@supports not (animation-timeline: view())` and `prefers-reduced-motion: reduce`.

## Copy

Short declarative lines, one idea each, in the register used by Hadrian and Path Robotics:
a step name, one sentence, one hard fact. Every fact is checked against
`replay/assets/traj.json` (the recorded run) rather than invented.

## Design

Built against the `design-taste-frontend` skill.

- Dials: DESIGN_VARIANCE 7, MOTION_INTENSITY 6, VISUAL_DENSITY 3
- Theme: light, locked. Radius: all-sharp (0).
- Palette: `--accent #a85a2c` sampled from the robot arms in the hero render, plus
  `--s2 #2d5f78` and `--s3 #8d7230` for the parts. All under 80% saturation, all >= 4.4:1.
- Type: Geist variable, self-hosted. No third-party requests on any page.

Local preview:

    python3 -m http.server 4173

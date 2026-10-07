"""Smooth the sampled motion keyframes in styles.css.

The parts, lines and the finished robot follow the scroll through keyframes sampled along their paths
(61 for the parts and lines, 25 for the robot). Between samples the browser interpolates in straight
segments, so speed changes slightly at every joint. This resamples each such block 4x with monotone cubic
interpolation (it passes through every original sample and never overshoots), so the motion keeps its
exact route and timing but loses the steps. Blocks that are already dense are left alone, so it is safe to
run after every change (gen-mobile.py calls it).

    python3 scripts/smooth-keyframes.py
"""
import re

FACTOR = 4
LINE = re.compile(r'^\s*([\d.]+)% \{ (offset-distance|stroke-dashoffset): (-?[\d.]+)(%?);')


def pchip(xs, ys, x):
    """Monotone cubic (Fritsch-Carlson) value at x."""
    n = len(xs)
    h = [xs[i + 1] - xs[i] for i in range(n - 1)]
    d = [(ys[i + 1] - ys[i]) / h[i] for i in range(n - 1)]
    m = [0.0] * n
    if n > 2:
        for i in range(1, n - 1):
            if d[i - 1] * d[i] > 0:
                w1, w2 = 2 * h[i] + h[i - 1], h[i] + 2 * h[i - 1]
                m[i] = (w1 + w2) / (w1 / d[i - 1] + w2 / d[i])
        m[0] = ((2 * h[0] + h[1]) * d[0] - h[0] * d[1]) / (h[0] + h[1]) if n > 2 else d[0]
        if m[0] * d[0] <= 0:
            m[0] = 0.0
        elif d[0] * d[1] <= 0 and abs(m[0]) > 3 * abs(d[0]):
            m[0] = 3 * d[0]
        m[-1] = ((2 * h[-1] + h[-2]) * d[-1] - h[-1] * d[-2]) / (h[-1] + h[-2]) if n > 2 else d[-1]
        if m[-1] * d[-1] <= 0:
            m[-1] = 0.0
        elif d[-1] * d[-2] <= 0 and abs(m[-1]) > 3 * abs(d[-1]):
            m[-1] = 3 * d[-1]
    else:
        m = [d[0], d[0]]
    i = max(0, min(n - 2, next((k for k in range(n - 1) if xs[k] <= x <= xs[k + 1]), n - 2)))
    t = (x - xs[i]) / h[i]
    h00, h10, h01, h11 = 2*t**3 - 3*t**2 + 1, t**3 - 2*t**2 + t, -2*t**3 + 3*t**2, t**3 - t**2
    return h00 * ys[i] + h10 * h[i] * m[i] + h01 * ys[i + 1] + h11 * h[i] * m[i + 1]


def smooth_block(match):
    name, body = match.group(1), match.group(2)
    rows = [LINE.match(l) for l in body.split('\n')]
    if not rows or any(r is None for r in rows) or not (12 <= len(rows) <= 70):
        return match.group(0)
    prop, unit = rows[0].group(2), rows[0].group(4)
    xs = [float(r.group(1)) for r in rows]
    ys = [float(r.group(3)) for r in rows]
    out = []
    for i in range(len(xs) - 1):
        for k in range(FACTOR):
            x = xs[i] + (xs[i + 1] - xs[i]) * k / FACTOR
            out.append((x, pchip(xs, ys, x)))
    out.append((xs[-1], ys[-1]))
    fmt = (lambda v: f'{v:.3f}%') if prop == 'offset-distance' else (lambda v: f'{v:.4f}')
    lines = [f'  {x:.2f}% {{ {prop}: {fmt(v)}; animation-timing-function: linear; }}' for x, v in out]
    return f'@keyframes {name} {{\n' + '\n'.join(lines) + '\n}'


def main(path='styles.css'):
    css = open(path).read()
    new, n = re.subn(r'@keyframes ([\w-]+) \{\n(.*?)\n\}', smooth_block, css, flags=re.S)
    open(path, 'w').write(new)
    print('smoothed' if new != css else 'already smooth')


if __name__ == '__main__':
    main()

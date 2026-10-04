import math
W = 1200
R, L, C = 820, 380, 600                 # line parks right, left, or centre

def square(cx, cy, s=23): return f'M{cx-s} {cy-s}h{2*s}v{2*s}h{-2*s}z'
def tri(cx, cy, s=25):    return f'M{cx} {cy-s}l{s} {int(1.7*s)}h{-2*s}z'
def circ(cx, cy, s=23):   return f'M{cx+s} {cy}a{s} {s} 0 1 1 {-2*s} 0a{s} {s} 0 1 1 {2*s} 0'
def hexa(cx, cy, s=29):   return f'M{cx} {cy-s}l{int(.87*s)} {s//2}v{s}l{-int(.87*s)} {s//2}l{-int(.87*s)} {-s//2}v{-s}z'
def pent(cx, cy, s=28):
    p=[(cx+s*math.sin(2*math.pi*i/5), cy-s*math.cos(2*math.pi*i/5)) for i in range(5)]
    return 'M'+'L'.join(f'{x:.0f} {y:.0f}' for x,y in p)+'z'

def arm(bx, by, ex, ey, wx, wy, cls, d):
    g = 1 if wx > ex else -1
    return (f'  <g class="arm {cls}" style="--d:{d:.2f}s">\n'
            f'    <path d="M{bx-36} {by}h72"/><path d="M{bx} {by}L{ex} {ey}"/>\n'
            f'    <g class="reach"><path d="M{ex} {ey}L{wx} {wy}"/>'
            f'<path d="M{wx} {wy}l{17*g} -12m{-17*g} 12l{13*g} 15"/></g>\n  </g>')

_seq = [0]
def rider(d, fn, fill, dur, delay, cls='rider'):
    """`dur`/`delay` are kept as the stagger seed; the part now advances with scroll, so
       each one gets its own slice of the stage timeline instead of its own clock."""
    i = _seq[0]; _seq[0] += 1
    a = (i * 9) % 40
    b = min(100, a + 62)
    return (f'  <g class="{cls}" style="offset-path:path(\'{d}\');--a:{a}%;--b:{b}%">'
            f'<g class="drift" style="animation-delay:{delay/1.7:.1f}s">'
            f'<path class="{fill}" d="{fn(0,0)}"/></g></g>')

def svg(h, body):
    return (f'<svg class="seg" viewBox="0 0 {W} {h}" fill="none" aria-hidden="true"\n'
            f'     stroke="currentColor" stroke-width="2.4" stroke-linecap="round" '
            f'stroke-linejoin="round">\n{body}\n</svg>')

# ---- 1. the parts, as drawings, playing around the middle of the page ----
PH = 1500
A = f'M{C-150} 0C{C-150} 180 {C+230} 200 {C+230} 380C{C+230} 560 {C-260} 560 {C-260} 740C{C-260} 920 {C+120} 940 {C+120} 1120C{C+120} 1260 700 1300 700 {PH}'
B = f'M{C} 0C{C} 160 {C-280} 190 {C-280} 390C{C-280} 580 {C+200} 600 {C+200} 780C{C+200} 950 {C-120} 980 {C-120} 1150C{C-120} 1280 820 1320 820 {PH}'
Bq = f'M{C+150} 0C{C+150} 200 {C-60} 230 {C-60} 420C{C-60} 620 {C+280} 640 {C+280} 820C{C+280} 980 {C} 1010 {C} 1170C{C} 1290 940 1330 940 {PH}'
play = svg(PH, '\n'.join([
    f'  <path class="lane d l1" pathLength="1" d="{A}"/>',
    f'  <path class="lane d l2" pathLength="1" d="{B}"/>',
    f'  <path class="lane d l3" pathLength="1" d="{Bq}"/>',
    rider(A, square, 'cad s1', 13, 0),   rider(A, circ, 'cad s3', 13, -6.5),
    rider(B, tri, 'cad s2', 14, -2),     rider(B, square, 'cad s1', 14, -9),
    rider(Bq, circ, 'cad s3', 15, -4),   rider(Bq, tri, 'cad s2', 15, -10)]))

# ---- 2. plan: they arrive on the right and get straightened ----
H = 1050
P1 = f'M700 0C700 200 {R-60} 240 {R-60} 440V{H}'
P2 = f'M820 0C820 200 {R} 240 {R} 440V{H}'
P3 = f'M940 0C940 200 {R+60} 240 {R+60} 440V{H}'
plan = svg(H, '\n'.join([
    f'  <path class="lane d l1" pathLength="1" d="{P1}"/>',
    f'  <path class="lane d l2" pathLength="1" d="{P2}"/>',
    f'  <path class="lane d l3" pathLength="1" d="{P3}"/>',
    rider(P1, square, 's1', 8, 0), rider(P2, tri, 's2', 8, -2.6), rider(P3, circ, 's3', 8, -5.2)]))

# ---- 3. tooling: no arms. A die per lane, cut to the negative of its part ----
TH = 1050
TX = (180, 360, 540)                     # lanes spread so each die has room
T1 = f'M{R-60} 0C{R-60} 240 {TX[0]} 300 {TX[0]} 560V{TH}'
T2 = f'M{R} 0C{R} 240 {TX[1]} 300 {TX[1]} 560V{TH}'
T3 = f'M{R+60} 0C{R+60} 240 {TX[2]} 300 {TX[2]} 560V{TH}'

def die(cx, cy, inner, cls, w=132):
    """A tool blank with the part's profile cut through it."""
    h = w // 2
    return (f'  <g class="die {cls}">\n'
            f'    <path class="blank" d="M{cx-h} {cy-h}h{w}v{w}h{-w}z"/>\n'
            f'    <path class="cut {cls}" d="{inner(cx, cy, 34)}"/>\n  </g>')

tooling = svg(TH, '\n'.join([
    f'  <path class="lane d l1" pathLength="1" d="{T1}"/>',
    f'  <path class="lane d l2" pathLength="1" d="{T2}"/>',
    f'  <path class="lane d l3" pathLength="1" d="{T3}"/>',
    die(TX[0], 760, square, 's1'),
    die(TX[1], 760, tri,    's2'),
    die(TX[2], 760, circ,   's3'),
    rider(T1, square, 's1', 9, 0), rider(T2, tri, 's2', 9, -3), rider(T3, circ, 's3', 9, -6)]))

# ---- 4. assemble: the lanes fan wide, then the original parts travel in and meet ----
AH = 1150
MX, CY = 700, 700                        # where everything lands
WIDE = (280, 700, 1120)                  # symmetric about MX
A1 = f'M180 0C180 180 {WIDE[0]} 250 {WIDE[0]} 420C{WIDE[0]} 580 {MX} 560 {MX} {CY}'
A2 = f'M360 0C360 200 {WIDE[1]} 260 {WIDE[1]} 420V{CY}'
A3 = f'M540 0C540 180 {WIDE[2]} 250 {WIDE[2]} 420C{WIDE[2]} 580 {MX} 560 {MX} {CY}'
assemble = svg(AH, '\n'.join([
    f'  <path class="lane d l1" pathLength="1" d="{A1}"/>',
    f'  <path class="lane d l2" pathLength="1" d="{A2}"/>',
    f'  <path class="lane d l3" pathLength="1" d="{A3}"/>',
    f'  <path class="lane d l4" pathLength="1" d="M{MX} {CY}V{AH}"/>',
    arm(MX-150, 1010, MX-116, 886, MX-62, 786, 'a1', -0.3),
    arm(MX+150, 1010, MX+116, 886, MX+62, 786, 'a2 flip', -1.8),
    # the parts themselves travel in from the wide points; no separate riders, so there is
    # one thing to watch instead of two
    '  <g class="merge m1">',
    f'    <path class="piece s1" style="--fx:-420px;--fy:-280px;--tx:-19px;--ty:10px" d="{square(MX, CY)}"/>',
    f'    <path class="piece s2" style="--fx:0px;--fy:-330px;--tx:0px;--ty:-17px" d="{tri(MX, CY)}"/>',
    f'    <path class="piece s3" style="--fx:420px;--fy:-280px;--tx:19px;--ty:10px" d="{circ(MX, CY)}"/>',
    f'    <path class="formed s1" d="{hexa(MX, CY)}"/>',
    '  </g>']))

# ---- 5. it jumps the line ----
SH = 900
FREE = f'M{L} 430C{L} 520 {L-210} 560 {L-210} {SH}'
ship = svg(SH, '\n'.join([
    f'  <path class="lane d l1" pathLength="1" d="M700 0C700 200 {L} 250 {L} 430"/>',
    f'  <path class="lane d l2 stop" pathLength="1" d="M{L-34} 430h68"/>',
    rider(FREE, hexa, 's1', 5.5, 0, 'rider leaves'),
    rider(FREE, pent, 's2', 5.5, -2.75, 'rider leaves')]))

for n, s in [('play', play), ('plan', plan), ('tooling', tooling),
             ('assemble', assemble), ('ship', ship)]:
    open(f'seg-{n}.svg', 'w').write(s)
    print(f'{n:9} paths {s.count(chr(60)+"path"):3}  riders {s.count(chr(34)+"rider")}')

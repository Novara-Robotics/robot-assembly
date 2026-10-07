import re,math
h=open('index.html').read(); c=open('styles.css').read()
def merge_desktop(h):
    m=re.search(r'    <!-- DESKTOP-LAYERS-START -->\n(.*?)    <!-- DESKTOP-LAYERS-END -->\n',h,flags=re.S)
    if not m: return h
    blk=m.group(1)
    a=re.search(r'(\s*<svg[^>]*>)(.*?)</svg>',blk,flags=re.S)           # lines layer
    b=re.search(r'</div>\s*(<svg[^>]*>)(.*?)</svg>',blk,flags=re.S)     # everything above the lines
    open_tag=a.group(1).strip()
    return h.replace(m.group(0),'    '+open_tag+a.group(2)+b.group(2)+'</svg>\n',1)
h=merge_desktop(h)
# ---- geometry (viewBox units; designed for a 390px phone: k=362/600)
W,Hm=600,4870; k=362/600; vh=844; lead=.62*vh; F=Hm*k; MY=3550
PM=round((MY*k-lead)/(F-vh)*100,1); END=98
def pct(y): return max(0,(y*k-lead)/(F-vh)*100)
LANES={
 'l1':'M150 0C150 120 450 150 450 290C450 430 200 450 200 590C200 690 190 720 190 800V1250C190 1330 130 1370 130 1450V2250C130 2480 50 2560 50 2800V3080C50 3280 300 3330 300 3550',
 'l2':'M300 0C300 110 120 150 120 280C120 420 430 440 430 580C430 690 300 730 300 800V3550',
 'l3':'M450 0C450 140 300 170 300 310C300 440 520 470 520 590C520 700 410 730 410 800V1250C410 1330 470 1370 470 1450V2250C470 2480 550 2560 550 2800V3080C550 3280 300 3330 300 3550'}
PRE={'p-a':'M420 -560C420 -300 150 -250 150 0','p-b':'M520 -420C520 -200 300 -240 300 0','p-c':'M350 -250C350 -120 450 -140 450 0'}
MADE='M300 3550V3850C300 4030 300 4150 300 4370'
# ---- markup
m=re.search(r'    <svg class="line".*?    </svg>\n',h,flags=re.S)
if m is None:
    h=re.sub(r'    <svg class="line-m".*?    </svg>\n','',h,flags=re.S)
    m=re.search(r'    <svg class="line line-d".*?    </svg>\n',h,flags=re.S); d_svg=m.group(0)
else:
    d_svg=m.group(0); h=h.replace(d_svg,d_svg.replace('<svg class="line"','<svg class="line line-d"',1)); d_svg=d_svg.replace('<svg class="line"','<svg class="line line-d"',1)
h=re.sub(r'    <!-- MOBILE-LAYERS-START -->.*?<!-- MOBILE-LAYERS-END -->\n','',h,flags=re.S)
if 'line-m' in h: h=re.sub(r'    <svg class="line line-m".*?    </svg>\n','',h,flags=re.S)
s=d_svg.replace('class="line line-d"','class="line line-m"').replace('viewBox="0 0 1200 5240"',f'viewBox="0 0 {W} {Hm}"')
s=s.replace('trail-fade','trail-fade-m').replace('id="trail"','id="trail-m"').replace('y1="-760"','y1="-600"').replace('x="-600" y="-1200" width="2400" height="7000"','x="-300" y="-1200" width="1200" height="7000"').replace('<rect x="-600" y="-1000" width="2400" height="1500"','<rect x="-300" y="-1000" width="1200" height="1500"')
for L,dd in LANES.items(): s=re.sub(rf'(class="lane d {L}"[^>]*? d=")[^"]*"',lambda mm:mm.group(1)+dd+'"',s)
for P_,pre in PRE.items():
    lane={'p-a':'l1','p-b':'l2','p-c':'l3'}[P_]
    s=re.sub(rf'(class="part {P_}" style="offset-path:path\(\')[^\']*\'',lambda mm:mm.group(1)+pre+LANES[lane][LANES[lane].index('C'):]+"'",s)
s=re.sub(r"(class=\"made\" style=\"offset-path:path\(')[^']*'",lambda mm:mm.group(1)+MADE+"'",s)
cx=iter([(-50,-1010),(-60,-1010),(-70,-1010)])
s=re.sub(r'<g class="die" transform="[^"]*"',lambda mm:'<g class="die" transform="translate(%d %d)"'%next(cx),s)
s=re.sub(r'(<g class="arm a\d[^"]*" style="[^"]*" transform=")[^"]*"',lambda mm:mm.group(1)+f'translate(-400 {MY-4200-90})"',s)
# two stacked layers: the lines, then a cheap fixed fade (CSS), then parts/dies/arms/robot.
# (A mask on the lines forced a full repaint every scroll frame; this fades the lines only, at no cost.)
open_tag=re.match(r'\s*<svg[^>]*>',s).group(0).strip()
lanes=re.search(r'<g class="lanes">.*?</g>',s,flags=re.S).group(0)
rest='\n      '+s[s.index(lanes)+len(lanes):s.rindex('</svg>')].strip()+'\n    '
layers=('    <!-- MOBILE-LAYERS-START -->\n    '+open_tag+'\n      '+lanes+'\n    </svg>\n'
        '    <div class="trail-fade" aria-hidden="true"></div>\n'
        '    '+open_tag.replace('class="line line-m"','class="line line-m line-m-top"')+rest+'</svg>\n    <!-- MOBILE-LAYERS-END -->\n')
def split_desktop(svg):
    open_tag=re.match(r'\s*<svg[^>]*>',svg).group(0).strip()
    lanes=re.search(r'<g class="lanes">.*?</g>',svg,flags=re.S).group(0)
    rest='\n      '+svg[svg.index(lanes)+len(lanes):svg.rindex('</svg>')].strip()+'\n    '
    return ('    <!-- DESKTOP-LAYERS-START -->\n    '+open_tag+'\n      '+lanes+'\n    </svg>\n'
            '    <div class="trail-fade-d" aria-hidden="true"><i></i></div>\n'
            '    '+open_tag.replace('class="line line-d"','class="line line-d line-d-top"')+rest+'</svg>\n    <!-- DESKTOP-LAYERS-END -->\n')
h=h.replace(d_svg,split_desktop(d_svg)+layers,1)
# captions classes, closing var
h=h.replace('<div class="say left" style="--at:21.9%">','<div class="say left c1" style="--at:21.9%">').replace('<div class="say right" style="--at:45.6%">','<div class="say right c2" style="--at:45.6%">').replace('<div class="say left" style="--at:68.3%">','<div class="say left c3" style="--at:68.3%">')
h=re.sub(r'<div class="say closing" style="[^"]*">',f'<div class="say closing" style="--at:94.1%;--at-m:{(MY+1060)/Hm*100:.1f}%">',h)
open('index.html','w').write(h)
# ---- keyframes
def parse(d):
    t=re.findall(r'[MCVL]|-?\d+\.?\d*',d); i=0; pts=[]; cur=None
    while i<len(t):
        kk=t[i]; i+=1
        if kk=='M': cur=(float(t[i]),float(t[i+1])); i+=2
        elif kk=='V':
            n=(cur[0],float(t[i])); i+=1
            pts+=[(cur[0],cur[1]+(n[1]-cur[1])*u/50) for u in range(51)]; cur=n
        elif kk=='C':
            p=[cur]+[(float(t[i+2*j]),float(t[i+2*j+1])) for j in range(3)]; i+=6
            for u in range(201):
                q=u/200;a=(1-q)**3;b=3*q*(1-q)**2;cc=3*q*q*(1-q);dd=q**3
                pts.append((a*p[0][0]+b*p[1][0]+cc*p[2][0]+dd*p[3][0],a*p[0][1]+b*p[1][1]+cc*p[2][1]+dd*p[3][1]))
            cur=p[3]
    cum=[0]
    for a,b in zip(pts,pts[1:]): cum.append(cum[-1]+math.dist(a,b))
    return pts,cum
def dist(pts,cum,y):
    m_=-1e9
    for p,d in zip(pts,cum):
        m_=max(m_,p[1])
        if m_>=y: return d/cum[-1]
    return 1.0
send=vh+PM/100*(F-vh); S=[send*i/60 for i in range(61)]
def kf(name,pts,cum,fmt,extra):
    o=f'@keyframes {name} {{\n'
    for i,ss in enumerate(S):
        f=dist(pts,cum,(ss-vh+lead)/k+extra)
        if i==60: f=1.0
        o+=f'  {ss/send*100:.2f}% {{ {fmt(f)}; animation-timing-function: linear; }}\n'
    return o+'}\n'
kfs=''
for n,P_,lane in (('a','p-a','l1'),('b','p-b','l2'),('c','p-c','l3')):
    pts,cum=parse(PRE[P_]+LANES[lane][LANES[lane].index('C'):])
    kfs+=kf(f'ride-{n}-m',pts,cum,lambda f:f'offset-distance: {f*100:.3f}%',0)
for n,lane in ((1,'l1'),(2,'l2'),(3,'l3')):
    pts,cum=parse(LANES[lane]); kfs+=kf(f'lane-m-{n}',pts,cum,lambda f:f'stroke-dashoffset: {1-f:.4f}',60)
pts,cum=parse(MADE); sE=vh+END/100*(F-vh)
kfs+='@keyframes ride-out-m {\n'
N=24
for i in range(N+1):
    t=i/N; ss=send+t*(sE-send); y=(ss-vh+lead)/k
    f=dist(pts,cum,y) if i<N else 1.0
    kfs+=f'  {t*100:.2f}% {{ offset-distance: {f*100:.3f}%; animation-timing-function: linear; }}\n'
kfs+='}\n'
Y0=(0-vh+lead)/k; Y1=(F-vh+lead)/k
caps={'c1':(850,1500),'c2':(1540,2340),'c3':(2390,4000)}
capcss=''.join(f'  .line-m ~ .say.{n} {{ animation-range: contain {pct(a):.1f}% contain {pct(b):.1f}%; }}\n' for n,(a,b) in caps.items())
block=f'''/* MOBILE-START (generated) */
.line-m {{ display: none; }}
.trail-fade {{ display: none; }}
@media (max-width: 900px) {{
  .line-d {{ display: none; }}
  .trail-fade-d {{ display: none; }}
  .line-m {{ display: block; }}
  .line-m-top {{ position: absolute; left: 0; top: 0; width: 100%; height: 100%; }}
  .hero {{ min-height: 60dvh; }}
  .line-m .part .fade {{ transform: scale(1.3); }}
  .line-m .made .bob > g {{ transform: scale(1.3) translate(0, 22px); }}
  .say.closing {{ position: absolute; top: var(--at-m); transform: translateY(-50%); left: 0; width: 100%; max-width: none; margin: 0; }}
  .say.closing h1 {{ font-size: clamp(2.3rem, 11vw, 3.4rem); }}
}}
@media (max-width: 900px) and (prefers-reduced-motion: no-preference) {{
  @supports (animation-timeline: view()) {{
    .line-m .l1 {{ animation-name: lane-m-1; animation-range: cover 0% contain {PM}%; }}
    .line-m .l2 {{ animation-name: lane-m-2; animation-range: cover 0% contain {PM}%; }}
    .line-m .l3 {{ animation-name: lane-m-3; animation-range: cover 0% contain {PM}%; }}
    .line-m .part {{ animation-name: ride-a-m, calm-m; animation-range: cover 0% contain {PM}%, cover 0% cover 4%; }}
    .line-m .p-b {{ animation-name: ride-b-m, calm-m; }}
    .line-m .p-c {{ animation-name: ride-c-m, calm-m; }}
    .line-m .part .shape {{ animation-range: contain 0% contain 4%; }}
    .line-m .part .piece {{ animation-range: contain {PM-4}% contain {PM}%; }}
    .line-m .part .fade {{ animation-range: contain {PM}% contain {PM+.2:.1f}%; }}
    .line-m .made {{
      animation-name: ride-out-m, arrive, walk-on, pace-on;
      animation-range: contain {PM}% contain {END}%, contain {PM}% contain {PM+.2:.1f}%, contain {PM}% contain {PM+1.6:.1f}%, contain 93% contain 97%;
    }}
    /* fade the lines out towards the top of the screen: a fixed page-coloured gradient between the line layer
       and the layer above it. Same stops and place as the old mask (fully faded above a, 22% visible at the
       middle stop, fully visible below b); the mask sat at 100dvh minus 1.8867 / 1.0867 flow widths (W = 100vw - 28px). */
    .trail-fade {{
      display: block; position: fixed; top: 0; left: 0; right: 0; height: calc(100dvh - 1.0867 * (100vw - 28px)); pointer-events: none;
      background: linear-gradient(to bottom, var(--bg) calc(100dvh - 1.8867 * (100vw - 28px)), rgb(252 252 252 / 0.78) calc(100dvh - 1.4067 * (100vw - 28px)), rgb(252 252 252 / 0) calc(100dvh - 1.0867 * (100vw - 28px)));
      opacity: 0; animation: trail-fade-in linear both; animation-timeline: --fl; animation-range: cover 4% cover 6%;
    }}
    /* on a phone the captions sit just under the header and change as the parts move on */
    .say.c1, .say.c2, .say.c3 {{
      position: fixed; top: 72px; bottom: auto; left: 20px; right: 20px; width: auto; margin: 0; transform: none;
      padding: 14px 0 34px; background: linear-gradient(to bottom, var(--bg) 62%, transparent);
      animation: cap linear both; animation-timeline: --fl;
    }}
    .say.c1 {{ animation-range: contain -12% contain {pct(caps['c1'][1]):.1f}%; }}
    .say.c2 {{ animation-range: contain {pct(caps['c2'][0]):.1f}% contain {pct(caps['c2'][1]):.1f}%; }}
    .say.c3 {{ animation-range: contain {pct(caps['c3'][0]):.1f}% contain {pct(caps['c3'][1]):.1f}%; }}
    .say .fact {{ font-size: 1rem; margin-top: 12px; }}
    /* the finished robot stands centred and sways a little, then comes back to the middle */
    .line-m .wander {{ animation: wander-m 12s ease-in-out infinite; }}
  }}
}}
@keyframes wander-m {{
  0%   {{ transform: translateX(0) scaleX(1); }}
  25%  {{ transform: translateX(calc(var(--pace) * 45px)) scaleX(1); }}
  30%  {{ transform: translateX(calc(var(--pace) * 45px)) scaleX(-1); }}
  70%  {{ transform: translateX(calc(var(--pace) * -45px)) scaleX(-1); }}
  75%  {{ transform: translateX(calc(var(--pace) * -45px)) scaleX(1); }}
  100% {{ transform: translateX(0) scaleX(1); }}
}}
@keyframes trail-fade-in {{ to {{ opacity: 1; }} }}
@keyframes calm-m {{ from {{ --amp: 0.5; }} to {{ --amp: 0; }} }}
@keyframes cap {{
  0% {{ opacity: 0; transform: translateY(14px); }}
  10%, 90% {{ opacity: 1; transform: none; }}
  100% {{ opacity: 0; transform: translateY(-10px); }}
}}
{kfs}/* MOBILE-END */
'''
c=re.sub(r'/\* MOBILE-START.*?MOBILE-END \*/\n','',c,flags=re.S).rstrip('\n')+'\n\n'+block
open('styles.css','w').write(c)
print('PM',PM,{n:(round(pct(a),1),round(pct(b),1)) for n,(a,b) in caps.items()})
import subprocess,sys
subprocess.run([sys.executable,'scripts/smooth-keyframes.py'],check=True)

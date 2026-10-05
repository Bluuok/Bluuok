"""Original profile badges and a snapshot-based contribution calendar.

The snake is decorative and follows calendar cells; it does not invent activity.
"""
import json
from pathlib import Path
import svgtext as ST

PALETTES = {
    'dark': {'ground':'#14202E','plane':'#2E4054','text':'#E8ECF0','muted':'#93A3B5','blue':'#5A8BE0','straw':'#E3B75E'},
    'light': {'ground':'#E9EDF1','plane':'#BCC7D3','text':'#17222E','muted':'#52606F','blue':'#2D5FB8','straw':'#A67A12'},
}

def txt(value,x,y,size,color,weight=450,anchor='start'):
    return f'<path fill="{color}" d="{ST.path(value,x,y,size,"plex",{"wght":weight},anchor=anchor)}"/>'

def frame(w,h,title,body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img"><title>{title}</title>{body}</svg>\n'

def badge(label,color):
    width=round(ST.measure(label,12.5,'plex',{'wght':500}))+22
    return frame(width,24,label,f'<rect width="{width}" height="24" rx="2" fill="{color}"/>'+txt(label,11,17,12.5,'#FFFFFF',500))

def folio_stats(mode,mobile=False):
    c=PALETTES[mode]
    w,h=(600,128) if mobile else (900,128)
    body=f'<rect width="{w}" height="{h}" rx="14" fill="{c["ground"]}"/>'
    for i,(n,label) in enumerate([('3','Merged PRs'),('1','Upstream project'),('2','Featured projects')]):
        cx=(i+.5)*w/3
        body+=txt(n,cx,58,40,c['text'],650,'middle')+txt(label,cx,94,18,c['muted'],450,'middle')
        if i: body+=f'<path d="M{i*w/3} 28 V100" stroke="{c["plane"]}"/>'
    return frame(w,h,'3 merged Folio PRs, 1 upstream project, 2 featured projects',body)

def calendar(mode,still=False):
    c=PALETTES[mode]
    data=json.loads((Path(__file__).parent/'contributions.json').read_text(encoding='utf-8'))
    colors=[c['plane'], '#335F88' if mode=='dark' else '#98B8D4', '#477CA9' if mode=='dark' else '#6E98BC', c['blue'], c['straw']]
    levels=['NONE','FIRST_QUARTILE','SECOND_QUARTILE','THIRD_QUARTILE','FOURTH_QUARTILE']
    body=f'<rect width="900" height="192" rx="14" fill="{c["ground"]}"/>'
    points=[]
    for x,week in enumerate(data['weeks']):
        for y,day in enumerate(week['contributionDays']):
            cx,cy=28+x*16,20+y*16
            color=colors[levels.index(day['contributionLevel'])]
            body+=f'<rect x="{cx}" y="{cy}" width="12" height="12" rx="2" fill="{color}"><title>{day["date"]}: {day["contributionCount"]} contributions</title></rect>'
        rows=range(len(week['contributionDays'])) if x%2==0 else reversed(range(len(week['contributionDays'])))
        points.extend((34+x*16,26+y*16) for y in rows)
    if not still:
        d='M'+' L'.join(f'{x} {y}' for x,y in points)
        body+=f'<path id="snake-path" d="{d}" fill="none"/>'
        for k in range(4,-1,-1):
            body+=f'<circle r="{5.8 if k==0 else 5.2}" fill="{c["straw"] if k==0 else c["blue"]}" opacity="{1-k*.12}"><animateMotion dur="42s" begin="-{42-k*.09:.2f}s" repeatCount="indefinite" calcMode="paced"><mpath href="#snake-path"/></animateMotion></circle>'
    body+=txt('Bluuok / contribution calendar',28,159,19,c['text'],550)
    body+=txt('Public GitHub snapshot · 2026-10-05',28,181,14,c['muted'])
    return frame(900,192,'Bluuok public contribution calendar snapshot on 2026-10-05; decorative snake animation',body)

def make_extras(assets):
    badges={'featured-threadcove':('Featured · ThreadCove','#A45220'),'featured-clawtide':('Featured · Clawtide','#2D5FB8'),'header-merged':('Folio · 3 merged PRs','#6E44A0'),'typescript':('TypeScript','#3178C6'),'react':('React','#287A8A'),'electron':('Electron','#47848F'),'bun':('Bun','#665B50'),'node':('Node.js','#4E853C'),'hono':('Hono','#B45422'),'sqlite':('SQLite','#36658B'),'mcp':('MCP','#6E44A0')}
    for name,(label,color) in badges.items():
        (assets/f'badge-{name}.svg').write_text(badge(label,color),encoding='utf-8')
    for mode in PALETTES:
        for mobile in (False,True):
            (assets/f'folio-stats{"-mobile" if mobile else ""}-{mode}.svg').write_text(folio_stats(mode,mobile),encoding='utf-8')
        for still in (False,True):
            (assets/f'contributions-{mode}{"-still" if still else ""}.svg').write_text(calendar(mode,still),encoding='utf-8')

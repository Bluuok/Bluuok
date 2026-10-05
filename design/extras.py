"""Original profile badges and verified Folio statistics.

Contribution snake artwork is generated separately by snake.mjs.
"""
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

def make_extras(assets):
    badges={'featured-threadcove':('Featured · ThreadCove','#A45220'),'featured-clawtide':('Featured · Clawtide','#2D5FB8'),'header-merged':('Folio · 3 merged PRs','#6E44A0'),'typescript':('TypeScript','#3178C6'),'react':('React','#287A8A'),'electron':('Electron','#47848F'),'bun':('Bun','#665B50'),'node':('Node.js','#4E853C'),'hono':('Hono','#B45422'),'sqlite':('SQLite','#36658B'),'mcp':('MCP','#6E44A0')}
    for name,(label,color) in badges.items():
        (assets/f'badge-{name}.svg').write_text(badge(label,color),encoding='utf-8')
    for mode in PALETTES:
        for mobile in (False,True):
            (assets/f'folio-stats{"-mobile" if mobile else ""}-{mode}.svg').write_text(folio_stats(mode,mobile),encoding='utf-8')

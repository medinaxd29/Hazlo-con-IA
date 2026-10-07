import json, os, shutil
from html import escape as e

DOMAIN = "https://hazloconia.es"   # <-- cambia aquí tu dominio final
NAME = "HazloConIA"
D = json.load(open("data.json"))
T, P, G = D["T"], D["P"], D["G"]
OUT = "dist"
shutil.rmtree(OUT, ignore_errors=True)
os.makedirs(OUT)
shutil.copy("style.css", f"{OUT}/style.css")

FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@600;800&family=Public+Sans:wght@400;500;600&display=swap" rel="stylesheet">'

def ld(o): return '<script type="application/ld+json">' + json.dumps(o, ensure_ascii=False) + '</script>'

def layout(title, desc, path, body, schemas=(), main_id="page"):
    url = DOMAIN + path
    return f'''<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website"><meta property="og:locale" content="es_ES">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{url}">
<meta name="twitter:card" content="summary">
{FONTS}<link rel="stylesheet" href="/style.css">
{''.join(ld(s) for s in schemas)}
</head><body><div class="wrap">
<header><a class="logo" href="/">Hazlo<span>ConIA</span></a><small>Herramientas de IA gratis, en español</small></header>
<main id="{main_id}">{body}</main>
<footer>{NAME} enlaza a webs de terceros y no está afiliada a ellas. Revisa siempre el resultado de la IA antes de usarlo.</footer>
</div></body></html>'''

def write(path, html):
    d = OUT + path
    os.makedirs(d, exist_ok=True)
    open(d + "index.html", "w", encoding="utf-8").write(html)

def card(t):
    s = P[t[0]][0]
    return (f'<article class="tool" data-s="{e((" ".join(t)).lower())}"><a class="task" href="/{s}/">Guía: {e(t[0])}</a>'
            f'<h3>{e(t[1])}</h3><p>{e(t[2])}</p><div class="row"><span class="badge">{e(t[4])}</span>'
            f'<a class="go" href="{t[3]}" target="_blank" rel="noopener noreferrer nofollow">Abrir {e(t[1])}</a></div></article>')

def crumbs(items):
    return ld({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": DOMAIN + u} for i, (n, u) in enumerate(items)]})

urls = ["/"]

# ---------- Home ----------
faq = [("¿Las herramientas son realmente gratis?", "Todas tienen un plan gratuito. Algunas limitan los usos diarios o exigen crear una cuenta; lo indicamos en cada tarjeta. Las condiciones pueden cambiar, así que confírmalas en la web de la herramienta."),
       ("¿Necesito saber de inteligencia artificial?", "No. Elige lo que quieres hacer y abre la herramienta. Casi todas funcionan escribiendo lo que necesitas en lenguaje normal."),
       ("¿Por qué estas herramientas y no otras?", "Priorizamos las que son gratis, funcionan en español y no piden tarjeta de crédito para empezar."),
       ("¿Puedo usar la IA con documentos personales?", "Evita subir datos sensibles como DNI, contratos o información de otras personas. Revisa siempre la política de privacidad de cada herramienta.")]
home = f'''<section class="hero"><h1>¿Qué quieres hacer hoy?</h1>
<p>Escribe la tarea o elígela abajo. Te llevamos a la mejor herramienta de IA gratuita para hacerla, sin buscar entre cientos.</p>
<div class="search"><input id="q" type="search" placeholder="Ej: hacer un CV, resumir un PDF, crear un logo" aria-label="Buscar tarea o herramienta" autocomplete="off"></div>
<div class="chips">{"".join(f'<a class="chip" href="/{v[0]}/">{e(k)}</a>' for k, v in P.items())}</div></section>
<p class="count" id="count">{len(T)} herramientas</p>
<div class="grid" id="grid">{"".join(card(t) for t in T)}</div>
<div class="empty" id="empty">No encontramos nada con esa búsqueda. Prueba con una palabra más corta, como “CV”, “PDF” o “imagen”.</div>
<section class="guides"><h2>Guías para empezar</h2><div class="links">{"".join(f'<a href="/guia/{g[0]}/">{e(g[1])}</a>' for g in G)}</div></section>
<section class="faq"><h2>Preguntas frecuentes</h2>{"".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in faq)}</section>
'''
SEARCH = r'''<script>var q=document.getElementById("q"),c=document.querySelectorAll(".tool"),n=document.getElementById("count"),em=document.getElementById("empty");
function f(s){return s.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g,"")}
q.addEventListener("input",function(){var v=f(q.value.trim()),k=0;c.forEach(function(x){var ok=!v||f(x.dataset.s).indexOf(v)>-1;x.hidden=!ok;if(ok)k++});n.textContent=k+(k==1?" herramienta":" herramientas");em.style.display=k?"none":"block"})</script>'''
home += SEARCH
write("/", layout(f"{NAME} · Herramientas de IA gratis para CV, PDF, imágenes y más",
    "Dinos qué quieres hacer y te llevamos a la mejor herramienta de IA gratuita: crear un CV, resumir un PDF, hacer una presentación, traducir documentos y más.",
    "/", home, [ld({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}),
        ld({"@context": "https://schema.org", "@type": "WebSite", "name": NAME, "url": DOMAIN + "/", "inLanguage": "es"})], "home"))

# ---------- Páginas de herramienta ----------
for k, (slug, h1, intro, steps, prompt) in P.items():
    path = f"/{slug}/"
    urls.append(path)
    body = (f'<nav class="crumb"><a href="/">Inicio</a> / {e(h1)}</nav><h1>{e(h1)}</h1><p class="lead">{e(intro)}</p>'
            f'<h2>Cómo hacerlo en 3 pasos</h2><ol class="steps">{"".join(f"<li>{e(s)}</li>" for s in steps)}</ol>'
            f'<h2>Herramientas gratuitas</h2><div class="grid">{"".join(card(t) for t in T if t[0] == k)}</div>'
            f'<h2>Prompt listo para copiar</h2><pre id="pr">{e(prompt)}</pre><button class="go" id="cp">Copiar prompt</button>'
            f'<h2>Otras tareas</h2><div class="links">{"".join(f"<a href=/{v[0]}/>{e(x)}</a>" for x, v in P.items() if x != k)}</div>'
            '<script>document.getElementById("cp").onclick=function(){var b=this;navigator.clipboard.writeText(document.getElementById("pr").textContent).then(function(){b.textContent="Copiado"},function(){b.textContent="Selecciona el texto y copia"})}</script>')
    write(path, layout(f"{h1} | {NAME}", intro, path, body, [crumbs([("Inicio", "/"), (h1, path)])]))

# ---------- Guías ----------
for slug, title, desc, content in G:
    path = f"/guia/{slug}/"
    urls.append(path)
    for p in P.values():
        content = content.replace(f"href='#/{p[0]}'", f"href='/{p[0]}/'")
    body = f'<nav class="crumb"><a href="/">Inicio</a> / Guías</nav><article class="art"><h1>{e(title)}</h1><p class="lead">{e(desc)}</p>{content}</article>'
    write(path, layout(f"{title} | {NAME}", desc, path, body, [
        crumbs([("Inicio", "/"), (title, path)]),
        ld({"@context": "https://schema.org", "@type": "Article", "headline": title, "description": desc, "inLanguage": "es", "mainEntityOfPage": DOMAIN + path})]))

# ---------- 404, sitemap, robots, README ----------
open(f"{OUT}/404.html", "w", encoding="utf-8").write(layout(f"Página no encontrada | {NAME}", "Esta página no existe.", "/404.html",
    '<h1>No encontramos esa página</h1><p class="lead">Puede que el enlace haya cambiado.</p><p><a class="go" href="/">Volver al inicio</a></p>'))
open(f"{OUT}/sitemap.xml", "w", encoding="utf-8").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
    "".join(f"<url><loc>{DOMAIN}{u}</loc></url>\n" for u in urls) + "</urlset>\n")
open(f"{OUT}/robots.txt", "w").write(f"User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml\n")
open(f"{OUT}/README.txt", "w", encoding="utf-8").write(f"""PUBLICAR {NAME}
1. Sube esta carpeta a Cloudflare Pages, Netlify o Vercel (gratis, sin configuración).
2. Conecta tu dominio. Si no es {DOMAIN}, edita DOMAIN en build.py y vuelve a ejecutar: python3 build.py
3. En Google Search Console añade tu dominio y envía {DOMAIN}/sitemap.xml
4. Para añadir una herramienta o guía, edita data.json y vuelve a ejecutar build.py
""")
shutil.copy("build.py", f"{OUT}/build.py"); shutil.copy("data.json", f"{OUT}/data.json")
print(len(urls), "páginas:", urls)

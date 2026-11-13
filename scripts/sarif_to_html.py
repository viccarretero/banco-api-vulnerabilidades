"""Convierte un archivo SARIF (resultado de DevSkim) en un reporte HTML.

Uso: python3 sarif_to_html.py <entrada.sarif> <salida.html> [herramienta]
"""
import html
import json
import sys
from collections import Counter
from datetime import datetime, timezone

NIVELES = {
    "error": ("Crítico", "#c62828"),
    "warning": ("Importante", "#ef6c00"),
    "note": ("Moderado", "#1565c0"),
    "none": ("Informativo", "#546e7a"),
}


def cargar_resultados(ruta):
    with open(ruta, encoding="utf-8-sig") as f:
        sarif = json.load(f)
    filas = []
    for run in sarif.get("runs", []):
        reglas = {}
        for regla in run.get("tool", {}).get("driver", {}).get("rules", []):
            reglas[regla.get("id")] = regla
        for r in run.get("results", []):
            regla = reglas.get(r.get("ruleId"), {})
            nivel = r.get("level") or regla.get("defaultConfiguration", {}).get("level", "warning")
            loc = (r.get("locations") or [{}])[0].get("physicalLocation", {})
            archivo = loc.get("artifactLocation", {}).get("uri", "-")
            linea = loc.get("region", {}).get("startLine", "-")
            nombre = regla.get("name") or regla.get("shortDescription", {}).get("text") or ""
            mensaje = r.get("message", {}).get("text") or nombre
            filas.append({
                "regla": r.get("ruleId", "-"),
                "nombre": nombre,
                "nivel": nivel,
                "mensaje": mensaje,
                "archivo": archivo,
                "linea": linea,
            })
    return filas


def generar_html(filas, herramienta="DevSkim"):
    conteo = Counter(f["nivel"] for f in filas)
    fecha = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    tarjetas = "".join(
        f'<div class="card" style="border-color:{color}"><span class="n">{conteo.get(k, 0)}</span>{etq}</div>'
        for k, (etq, color) in NIVELES.items()
    )
    cuerpo = "".join(
        "<tr>"
        f'<td><span class="tag" style="background:{NIVELES.get(f["nivel"], NIVELES["warning"])[1]}">'
        f'{NIVELES.get(f["nivel"], NIVELES["warning"])[0]}</span></td>'
        f'<td><code>{html.escape(str(f["regla"]))}</code><br><small>{html.escape(f["nombre"])}</small></td>'
        f'<td>{html.escape(f["mensaje"])}</td>'
        f'<td><code>{html.escape(str(f["archivo"]))}:{f["linea"]}</code></td>'
        "</tr>"
        for f in filas
    ) or '<tr><td colspan="4">Sin hallazgos 🎉</td></tr>'
    return f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Reporte {herramienta} - Banco API</title>
<style>
body{{font-family:system-ui,Segoe UI,Arial,sans-serif;margin:0;background:#f5f7fa;color:#1f2933}}
header{{background:#0b3d91;color:#fff;padding:24px 16px}}
header h1{{margin:0;font-size:1.5rem}} header p{{margin:6px 0 0;opacity:.85}}
main{{max-width:1100px;margin:0 auto;padding:16px}}
.cards{{display:flex;gap:12px;flex-wrap:wrap;margin:8px 0 20px}}
.card{{background:#fff;border-left:6px solid;padding:12px 16px;border-radius:8px;min-width:130px;box-shadow:0 1px 3px #0001}}
.card .n{{display:block;font-size:1.8rem;font-weight:700}}
.wrap{{overflow-x:auto;background:#fff;border-radius:8px;box-shadow:0 1px 3px #0001}}
table{{border-collapse:collapse;width:100%;font-size:.92rem}}
th,td{{padding:10px 12px;border-bottom:1px solid #e4e7eb;text-align:left;vertical-align:top}}
th{{background:#eef2f7}}
.tag{{color:#fff;padding:2px 8px;border-radius:10px;font-size:.8rem;white-space:nowrap}}
code{{font-size:.85rem}} small{{color:#52606d}}
</style></head><body>
<header><h1>Reporte de vulnerabilidades — {herramienta}</h1>
<p>Aplicación: Banco API (.NET 8) · Generado: {fecha} · Total de hallazgos: {len(filas)}</p></header>
<main>
<div class="cards">{tarjetas}</div>
<div class="wrap"><table>
<thead><tr><th>Severidad</th><th>Regla</th><th>Descripción</th><th>Ubicación</th></tr></thead>
<tbody>{cuerpo}</tbody></table></div>
<p><a href="resultados.sarif">Descargar resultados en formato SARIF</a> · <a href="../">Volver al inicio</a></p>
</main></body></html>"""


def main():
    if len(sys.argv) not in (3, 4):
        print(__doc__)
        sys.exit(1)
    filas = cargar_resultados(sys.argv[1])
    with open(sys.argv[2], "w", encoding="utf-8") as f:
        f.write(generar_html(filas, sys.argv[3] if len(sys.argv) == 4 else "DevSkim"))
    print(f"Reporte generado con {len(filas)} hallazgos: {sys.argv[2]}")


if __name__ == "__main__":
    main()

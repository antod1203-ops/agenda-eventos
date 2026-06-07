import json
import base64
import requests
from datetime import datetime

# --- CONFIGURACIÓN GLOBAL ---
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
TIMEOUT = 15

def extraer_url_limpia(url_completa):
    """
    Elimina prefijos de embed y decodifica Base64 de la URL si es necesario.
    """
    if not url_completa:
        return ""
    
    contenido_url = url_completa
    if "?r=" in url_completa:
        _, contenido_url = url_completa.split("?r=", 1)
        
    contenido_url = contenido_url.strip()
    
    if contenido_url.startswith(("http://", "https://")):
        return contenido_url
        
    try:
        b64_fixed = contenido_url + "=" * ((4 - len(contenido_url) % 4) % 4)
        return base64.b64decode(b64_fixed).decode('utf-8', errors='ignore').strip()
    except Exception:
        return contenido_url

def obtener_categoria_optima(titulo, cat_original):
    """
    Analiza el título mediante palabras clave detalladas para asignar el deporte correcto.
    Evita falsos positivos aislando términos genéricos como 'vs'.
    """
    titulo_lower = titulo.lower()
    
    # Diccionario altamente específico para evitar solapamientos incorrectos
    keywords = {
        "F1": [
            "f1", "formula 1", "formula uno", "gp ", "grand prix", 
            "verstappen", "hamilton", "leclerc", "alonso", "perez", "sainz"
        ],
        "Tenis": [
            "roland garros", "tenis", "tennis", "wimbledon", "atp", "wta", 
            "us open", "australian open", "nadal", "alcaraz", "djokovic", 
            "sinner", "itf", "challenger", "masters 1000"
        ],
        "Béisbol": [
            "mlb", "béisbol", "beisbol", "giants", "cubs", "yankees", "dodgers", 
            "red sox", "astros", "lidom", "lbpv", "home run", "world series"
        ],
        "Baloncesto": [
            "nba", "básquet", "basquet", "basketball", "euroleague", "euroliga", 
            "acb", "fiba", "wnba", "lakers", "celtics", "warriors", "bulls"
        ],
        "UFC/MMA": [
            "ufc", "mma", "bellator", "pfl", "one championship", "knockout", 
            "ko/tko", "main card", "prelims", "pesajes"
        ],
        "MotoGP": [
            "motogp", "moto2", "moto3", "superbike", "marquez", "bagnaia", "quartararo"
        ],
        "Ciclismo": [
            "tour de france", "giro d'italia", "vuelta a españa", "ciclismo", "cycling",
            "uci worldtour", "pogačar", "vingegaard"
        ],
        "Fútbol": [
            "laliga", "premier league", "serie a", "bundesliga", "ligue 1",
            "champions league", "ucl", "europa league", "libertadores", "sudamericana",
            "mls", "liga mx", "ligamx", "fifa", "uefa", "conmebol", "real madrid", 
            "barcelona", "manchester", "juventus", "psg", "boca juniors", "river plate"
        ]
    }
    
    # 1. Intento emparejar con las palabras clave ultra específicas
    for categoria, claves in keywords.items():
        if any(clave in titulo_lower for clave in claves):
            return categoria
        
    # 2. Filtro secundario: Si no es específico pero tiene "vs", suele ser fútbol no listado arriba
    if "vs" in titulo_lower or " v " in titulo_lower:
        return "Fútbol"
        
    # 3. Plan de rescate basado en la categoría original del JSON externo
    if not cat_original or cat_original.lower() in ["other", "futbol", "otros"]:
        return "Otros Deportes"
        
    return cat_original.capitalize()

def _fetch_json(session, url):
    """Realiza la petición HTTP segura y retorna el JSON si es exitosa."""
    try:
        print(f"Descargando desde: {url}...")
        response = session.get(url, headers=DEFAULT_HEADERS, timeout=TIMEOUT)
        if response.status_code == 200:
            return response.json()
        print(f"Error {response.status_code} al conectar con {url}")
    except Exception as e:
        print(f"No se pudo acceder a {url}. Error: {e}")
    return None

# --- PARSERS ESPECÍFICOS PARA CADA ENDPOINT ---

def _parse_streamtp(data, fecha_defecto):
    eventos = []
    for item in data:
        titulo = " ".join(item.get("title", "").split()).strip()
        link_final = extraer_url_limpia(item.get("link", ""))
        canal_sugerido = link_final.split("stream=")[-1].upper() if "stream=" in link_final else ""
        
        eventos.append({
            "title": titulo,
            "fecha": item.get("fecha", fecha_defecto),
            "time": item.get("time", "00:00"),
            "category": obtener_categoria_optima(titulo, item.get("category", "")),
            "link": link_final,
            "nombre": canal_sugerido if canal_sugerido else item.get("language", "").capitalize()
        })
    return eventos

def _parse_la18hd(data, fecha_defecto):
    eventos = []
    for item in data:
        titulo = " ".join(item.get("title", "").split()).strip()
        link_final = extraer_url_limpia(item.get("link", ""))
        canal_sugerido = link_final.split("stream=")[-1].capitalize() if "stream=" in link_final else ""
        
        eventos.append({
            "title": titulo,
            "fecha": item.get("date", item.get("fecha", fecha_defecto)),
            "time": item.get("time", "00:00"),
            "category": obtener_categoria_optima(titulo, item.get("category", "")),
            "link": link_final,
            "nombre": canal_sugerido if canal_sugerido else item.get("language", "")
        })
    return eventos

def _parse_streamhdx(data, fecha_defecto):
    eventos = []
    for dia in data.get("dias", []):
        fecha_iso = dia.get("fecha_iso", fecha_defecto)
        for ev in dia.get("eventos", []):
            titulo = " ".join(ev.get("titulo", "").split()).strip()
            cat_orig = ev.get("categoria", "")
            
            for canal in ev.get("canales", []):
                eventos.append({
                    "title": titulo,
                    "fecha": fecha_iso,
                    "time": ev.get("hora", "00:00"),
                    "category": obtener_categoria_optima(titulo, cat_orig),
                    "link": extraer_url_limpia(canal.get("url", "")),
                    "nombre": canal.get("nombre", "").strip()
                })
    return eventos

def _parse_pltvhd(data, fecha_defecto):
    eventos = []
    for item in data.get("data", []):
        attrs = item.get("attributes", {})
        titulo = " ".join(attrs.get("diary_description", "").split()).strip()
        
        hora_corta = "00:00"
        if attrs.get("diary_hour"):
            hora_corta = ":".join(attrs["diary_hour"].split(":")[:2])
            
        fecha_evento = attrs.get("date_diary", fecha_defecto)
        pais_idioma = attrs.get("country", {}).get("data", {}).get("attributes", {}).get("name", "")
        embeds = attrs.get("embeds", {}).get("data", [])
        
        if embeds:
            for emb in embeds:
                emb_attr = emb.get("attributes", {})
                eventos.append({
                    "title": titulo,
                    "fecha": fecha_evento,
                    "time": hora_corta,
                    "category": obtener_categoria_optima(titulo, ""),
                    "link": extraer_url_limpia(emb_attr.get("embed_iframe", "")),
                    "nombre": emb_attr.get("embed_name", "").strip() or pais_idioma
                })
        else:
            eventos.append({
                "title": titulo,
                "fecha": fecha_evento,
                "time": hora_corta,
                "category": obtener_categoria_optima(titulo, ""),
                "link": "",
                "nombre": pais_idioma
            })
    return eventos

# --- PROCESADOR CENTRAL ---

def procesar_agendas_web(fecha_por_defecto="2026-06-07"):
    eventos_normalizados = []
    
    # Registro de endpoints mapeados con su respectivo analizador de estructura
    endpoints = [
        {"url": "https://streamtp-x-y-z.ws/eventos.json", "parser": _parse_streamtp},
        {"url": "https://la18hd.com//eventos/json/agenda123.json", "parser": _parse_la18hd},
        {"url": "https://streamhdx.com//eventos.json", "parser": _parse_streamhdx},
        {"url": "https://pltvhd.com/diaries.json", "parser": _parse_pltvhd}
    ]
    
    # Uso de Session para mantener vivas las conexiones TCP (Keep-Alive) y acelerar peticiones
    with requests.Session() as session:
        for target in endpoints:
            data = _fetch_json(session, target["url"])
            if data:
                try:
                    eventos_extraidos = target["parser"](data, fecha_por_defecto)
                    eventos_normalizados.extend(eventos_extraidos)
                except Exception as parse_err:
                    print(f"Error procesando el formato interno de {target['url']}: {parse_err}")

    # Ordenamiento global estricto: 1º Fecha, 2º Hora, 3º Título alfabético
    print("\nOrganizando y ordenando los eventos globalmente...")
    eventos_ordenados = sorted(
        eventos_normalizados,
        key=lambda x: (x["fecha"], x["time"], x["title"].lower())
    )

    # Escritura del archivo JSON de salida
    archivo_salida = 'eventos.json'
    with open(archivo_salida, 'w', encoding='utf-8') as f:
        json.dump(eventos_ordenados, f, ensure_ascii=False, indent=4)
        
    print(f"\n[Proceso Completado con Éxito]")
    print(f"Se han extraído de la web y organizado {len(eventos_ordenados)} transmisiones.")
    print(f"Resultado final guardado en el archivo local: '{archivo_salida}'")

if __name__ == "__main__":
    # Obtiene automáticamente la fecha de hoy en formato AAAA-MM-DD (ej: "2026-06-07")
    fecha_hoy_automatica = datetime.now().strftime("%Y-%m-%d")

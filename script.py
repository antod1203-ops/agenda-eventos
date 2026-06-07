import json
import base64
import requests
from datetime import datetime

def extraer_url_limpia(url_completa):
    """
    Elimina por completo cualquier prefijo de embed dejando solo la URL directa.
    Si el parámetro 'r=' viene codificado en Base64, lo decodifica automáticamente.
    """
    if not url_completa:
        return ""
    
    contenido_url = url_completa
    
    if "?r=" in url_completa:
        _, contenido_url = url_completa.split("?r=", 1)
        
    contenido_url = contenido_url.strip()
    
    if contenido_url.startswith("http://") or contenido_url.startswith("https://"):
        return contenido_url
        
    try:
        b64_fixed = contenido_url + "=" * ((4 - len(contenido_url) % 4) % 4)
        url_decodificada = base64.b64decode(b64_fixed).decode('utf-8', errors='ignore')
        return url_decodificada.strip()
    except Exception:
        return contenido_url

def obtener_categoria_optima(titulo, cat_original):
    """
    Analiza el título mediante palabras clave para asignar la categoría deportiva correcta.
    """
    titulo_lower = titulo.lower()
    
    if "f1" in titulo_lower or "formula 1" in titulo_lower or "gp " in titulo_lower:
        return "F1"
    elif "roland garros" in titulo_lower or "tenis" in titulo_lower or "tennis" in titulo_lower:
        return "Tenis"
    elif "mlb" in titulo_lower or "béisbol" in titulo_lower or "beisbol" in titulo_lower or "giants" in titulo_lower or "cubs" in titulo_lower:
        return "Béisbol"
    elif "nba" in titulo_lower or "básquet" in titulo_lower or "basquet" in titulo_lower:
        return "Baloncesto"
    elif "ufc" in titulo_lower or "mma" in titulo_lower:
        return "UFC/MMA"
    elif "amistoso" in titulo_lower or "copa" in titulo_lower or "liga" in titulo_lower or "división" in titulo_lower or "vs" in titulo_lower:
        return "Fútbol"
        
    if not cat_original or cat_original.lower() in ["other", "futbol"]:
        return "Fútbol" if "vs" in titulo_lower else "Otros Deportes"
        
    return cat_original.capitalize()

def procesar_agendas_web(fecha_por_defecto="2026-06-07"):
    eventos_normalizados = []
    
    # Cabeceras para simular una petición desde el navegador y evitar bloqueos (403 Forbidden)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    # --- 1. PROCESAR: https://streamtp-x-y-z.ws/eventos.json ---
    url1 = "https://streamtp-x-y-z.ws/eventos.json"
    try:
        print(f"Descargando desde: {url1}...")
        response = requests.get(url1, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            for item in data:
                titulo = " ".join(item.get("title", "").split()).strip()
                link_final = extraer_url_limpia(item.get("link", ""))
                
                canal_sugerido = ""
                if "stream=" in link_final:
                    canal_sugerido = link_final.split("stream=")[-1].upper()

                eventos_normalizados.append({
                    "title": titulo,
                    "fecha": item.get("fecha", fecha_por_defecto),
                    "time": item.get("time", "00:00"),
                    "category": obtener_categoria_optima(titulo, item.get("category", "")),
                    "link": link_final,
                    "nombre": canal_sugerido if canal_sugerido else item.get("language", "").capitalize()
                })
        else:
            print(f"Error {response.status_code} al conectar con {url1}")
    except Exception as e:
        print(f"No se pudo acceder a {url1}. Error: {e}")

    # --- 2. PROCESAR: https://la18hd.com//eventos/json/agenda123.json ---
    url2 = "https://la18hd.com//eventos/json/agenda123.json"
    try:
        print(f"Descargando desde: {url2}...")
        response = requests.get(url2, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            for item in data:
                titulo = " ".join(item.get("title", "").split()).strip()
                link_final = extraer_url_limpia(item.get("link", ""))
                
                canal_sugerido = ""
                if "stream=" in link_final:
                    canal_sugerido = link_final.split("stream=")[-1].capitalize()

                eventos_normalizados.append({
                    "title": titulo,
                    "fecha": item.get("date", item.get("fecha", fecha_por_defecto)),
                    "time": item.get("time", "00:00"),
                    "category": obtener_categoria_optima(titulo, item.get("category", "")),
                    "link": link_final,
                    "nombre": canal_sugerido if canal_sugerido else item.get("language", "")
                })
        else:
            print(f"Error {response.status_code} al conectar con {url2}")
    except Exception as e:
        print(f"No se pudo acceder a {url2}. Error: {e}")

    # --- 3. PROCESAR: https://streamhdx.com//eventos.json ---
    url3 = "https://streamhdx.com//eventos.json"
    try:
        print(f"Descargando desde: {url3}...")
        response = requests.get(url3, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            for dia in data.get("dias", []):
                fecha_iso = dia.get("fecha_iso", fecha_por_defecto)
                for ev in dia.get("eventos", []):
                    titulo = " ".join(ev.get("titulo", "").split()).strip()
                    categoria_original = ev.get("categoria", "")
                    
                    for canal in ev.get("canales", []):
                        link_final = extraer_url_limpia(canal.get("url", ""))
                        eventos_normalizados.append({
                            "title": titulo,
                            "fecha": fecha_iso,
                            "time": ev.get("hora", "00:00"),
                            "category": obtener_categoria_optima(titulo, categoria_original),
                            "link": link_final,
                            "nombre": canal.get("nombre", "").strip()
                        })
        else:
            print(f"Error {response.status_code} al conectar con {url3}")
    except Exception as e:
        print(f"No se pudo acceder a {url3}. Error: {e}")

    # --- 4. PROCESAR: https://pltvhd.com/diaries.json ---
    url4 = "https://pltvhd.com/diaries.json"
    try:
        print(f"Descargando desde: {url4}...")
        response = requests.get(url4, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            for item in data.get("data", []):
                attrs = item.get("attributes", {})
                titulo = " ".join(attrs.get("diary_description", "").split()).strip()
                
                hora_completa = attrs.get("diary_hour", "00:00")
                hora_corta = ":".join(hora_completa.split(":")[:2]) if hora_completa else "00:00"
                
                fecha_evento = attrs.get("date_diary", fecha_por_defecto)
                pais_idioma = attrs.get("country", {}).get("data", {}).get("attributes", {}).get("name", "")
                
                embeds = attrs.get("embeds", {}).get("data", [])
                
                if embeds:
                    for emb in embeds:
                        embed_attr = emb.get("attributes", {})
                        nombre_canal = embed_attr.get("embed_name", "").strip()
                        iframe_url = embed_attr.get("embed_iframe", "")
                        link_final = extraer_url_limpia(iframe_url)
                        
                        eventos_normalizados.append({
                            "title": titulo,
                            "fecha": fecha_evento,
                            "time": hora_corta,
                            "category": obtener_categoria_optima(titulo, ""),
                            "link": link_final,
                            "nombre": nombre_canal if nombre_canal else pais_idioma
                        })
                else:
                    eventos_normalizados.append({
                        "title": titulo,
                        "fecha": fecha_evento,
                        "time": hora_corta,
                        "category": obtener_categoria_optima(titulo, ""),
                        "link": "",
                        "nombre": pais_idioma
                    })
        else:
            print(f"Error {response.status_code} al conectar con {url4}")
    except Exception as e:
        print(f"No se pudo acceder a {url4}. Error: {e}")

    # --- ORDENAMIENTO ESTRICTO ---
    # Prioridad: 1º Fecha (Asc), 2º Hora (Asc), 3º Título (Alfabético)
    print("\nOrganizando y ordenando los eventos globalmente...")
    eventos_ordenados = sorted(
        eventos_normalizados,
        key=lambda x: (x["fecha"], x["time"], x["title"].lower())
    )

    # --- GUARDAR EN EL JSON FINAL ---
    archivo_salida = 'eventos.json'
    with open(archivo_salida, 'w', encoding='utf-8') as f:
        json.dump(eventos_ordenados, f, ensure_ascii=False, indent=4)
        
    print(f"\n[Proceso Completado con Éxito]")
    print(f"Se han extraído de la web y organizado {len(eventos_ordenados)} transmisiones.")
    print(f"Resultado final guardado en el archivo local: '{archivo_salida}'")

if __name__ == "__main__":
    # Puedes ajustar la fecha por defecto si algún evento web viene sin el campo estructurado
    procesar_agendas_web(fecha_por_defecto="2026-06-07")

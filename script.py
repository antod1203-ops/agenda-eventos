import json
import base64
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

def procesar_agendas(fecha_por_defecto="2026-06-07"):
    eventos_normalizados = []

    # --- 1. PROCESAR: streamtp-x-y-z.ws/eventos.json ---
    try:
        with open('eventos.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            for item in data:
                titulo = " ".join(item.get("title", "").split()).strip()
                link_final = extraer_url_limpia(item.get("link", ""))
                
                # Extraer nombre del canal desde el parámetro stream=
                canal_sugerido = ""
                if "stream=" in link_final:
                    canal_sugerido = link_final.split("stream=")[-1].upper()

                eventos_normalizados.append({
                    "title": titulo,
                    "fecha": item.get("fecha", fecha_por_defecto),
                    "time": item.get("time", "00:00"),
                    "category": obtener_categoria_optima(titulo, item.get("category", "")),
                    "link": link_final,
                    # CAMBIO: Ahora se guarda bajo la clave "nombre"
                    "nombre": canal_sugerido if canal_sugerido else item.get("language", "").capitalize()
                })
    except FileNotFoundError:
        pass

    # --- 2. PROCESAR: la18hd.com/eventos/json/agenda123.json ---
    try:
        with open('agenda123.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
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
                    # CAMBIO: Ahora se guarda bajo la clave "nombre"
                    "nombre": canal_sugerido if canal_sugerido else item.get("language", "")
                })
    except FileNotFoundError:
        pass

    # --- 3. PROCESAR: streamhdx.com/eventos.json ---
    try:
        with open('eventos (1).json', 'r', encoding='utf-8') as f:
            data = json.load(f)
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
                            # CAMBIO: Mapeo directo del nombre del canal original
                            "nombre": canal.get("nombre", "").strip()
                        })
    except FileNotFoundError:
        pass

    # --- 4. PROCESAR: pltvhd.com/diaries.json (Estructura Strapi) ---
    try:
        with open('diaries.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
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
                            # CAMBIO: Mapeo directo del canal de la base de datos
                            "nombre": nombre_canal if nombre_canal else pais_idioma
                        })
                else:
                    eventos_normalizados.append({
                        "title": titulo,
                        "fecha": fecha_evento,
                        "time": hora_corta,
                        "category": obtener_categoria_optima(titulo, ""),
                        "link": "",
                        # CAMBIO: Respaldo de idioma bajo la clave "nombre"
                        "nombre": pais_idioma
                    })
    except FileNotFoundError:
        pass

    # --- ORDENAMIENTO ESTRICTO ---
    # 1º Fecha (Asc), 2º Hora (Asc), 3º Título (Alfabético)
    eventos_ordenados = sorted(
        eventos_normalizados,
        key=lambda x: (x["fecha"], x["time"], x["title"].lower())
    )

    # --- GUARDAR EN EL JSON FINAL ---
    archivo_salida = 'eventos.json'
    with open(archivo_salida, 'w', encoding='utf-8') as f:
        json.dump(eventos_ordenados, f, ensure_ascii=False, indent=4)
        
    print(f"\n[Proceso Completado]")
    print(f"Se han organizado {len(eventos_ordenados)} transmisiones con la clave 'nombre'.")
    print(f"Resultado estructurado correctamente en: '{archivo_salida}'")

if __name__ == "__main__":
    procesar_agendas(fecha_por_defecto="2026-06-07")

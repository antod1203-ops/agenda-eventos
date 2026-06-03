import requests
import json

def limpiar_categoria(category):
    if not category:
        return ""
    category_str = str(category).strip().lower()
    if "futbol" in category_str or "fútbol" in category_str:
        return "Futbol"
    return str(category).strip()

def extraer_y_organizar_eventos():
    urls = [
        "https://la14hd.com/eventos/json/agenda123.json",
        "https://streamtp-x-y-z.ws/eventos.json"
    ]
    
    eventos_consolidados = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    for url in urls:
        try:
            print(f"Conectando a: {url}...")
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            eventos_lista = []
            if isinstance(data, list):
                eventos_lista = data
            elif isinstance(data, dict):
                for clave, valor in data.items():
                    if isinstance(valor, list):
                        eventos_lista = valor
                        break
                if not eventos_lista:
                    eventos_lista = [data]
            
            for item in eventos_lista:
                title = item.get("title") or item.get("nombre") or item.get("evento") or ""
                time = item.get("time") or item.get("hora") or item.get("inicio") or ""
                category = item.get("category") or item.get("categoria") or item.get("deporte") or ""
                status = item.get("status") or item.get("estado") or ""
                link = item.get("link") or item.get("url") or item.get("stream") or ""
                language = item.get("language") or item.get("idioma") or ""
                
                category_limpia = limpiar_categoria(category)
                
                evento_formateado = {
                    "title": str(title).strip(),
                    "time": str(time).strip(),
                    "category": category_limpia,
                    "status": str(status).strip(),
                    "link": str(link).strip(),
                    "language": str(language).strip()
                }
                eventos_consolidados.append(evento_formateado)
                
        except Exception as e:
            print(f"Error con {url}: {e}")

    # CAMBIO: Guardamos como .json para que Blogger lo lea de forma nativa
    archivo_salida = "eventos_organizados.json"
    try:
        with open(archivo_salida, "w", encoding="utf-8") as f:
            json.dump(eventos_consolidados, f, indent=4, ensure_ascii=False)
        print(f"\n¡Éxito! Guardados {len(eventos_consolidados)} eventos.")
    except IOError as e:
        print(f"Error al escribir: {e}")

if __name__ == "__main__":
    extraer_y_organizar_eventos()
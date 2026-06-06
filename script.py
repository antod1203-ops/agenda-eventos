import requests
import json

def limpiar_categoria(category):
    if category and "futbol" in str(category).lower():
        return "Futbol"
    return str(category).strip() if category else ""

def extraer_y_organizar_eventos():
    urls = [
        "http://la18hd.com//eventos/json/agenda123.json",
        "https://streamtp-x-y-z.ws/eventos.json"
    ]
    
    eventos_consolidados = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    for url in urls:
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            # Al ser una lista directa de eventos, iteramos directamente
            for item in response.json():
                eventos_consolidados.append({
                    "title": str(item.get("title") or item.get("nombre") or "").strip(),
                    "time": str(item.get("time") or item.get("hora") or "").strip(),
                    "category": limpiar_categoria(item.get("category") or item.get("categoria")),
                    "status": str(item.get("status") or "").strip(),
                    "link": str(item.get("link") or item.get("url") or "").strip(),
                    "language": str(item.get("language") or "").strip()
                })
        except Exception as e:
            print(f"Error con {url}: {e}")

    try:
        with open("eventos.json", "w", encoding="utf-8") as f:
            json.dump(eventos_consolidados, f, indent=4, ensure_ascii=False)
        print(f"Éxito: Guardados {len(eventos_consolidados)} eventos.")
    except IOError as e:
        print(f"Error al escribir: {e}")

if __name__ == "__main__":
    extraer_y_organizar_eventos()

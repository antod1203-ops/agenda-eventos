import requests
import json

def limpiar_categoria(category):
    if not category:
        return ""
    
    # Convertimos a string y pasamos a minúsculas para una comparación flexible
    category_str = str(category).strip().lower()
    
    # Si contiene la palabra "futbol" o "fútbol", lo agrupamos en "Futbol"
    if "futbol" in category_str or "fútbol" in category_str:
        return "Futbol"
        
    # Si no es fútbol, mantiene su nombre original
    return str(category).strip()

def extraer_y_organizar_eventos():
    urls = [
        "https://la14hd.com/eventos/json/agenda123.json",
        "https://streamtp-abc.net/eventos.json"
    ]
    
    eventos_consolidados = []
    
    # User-Agent para simular una petición desde el navegador y evitar bloqueos de Cloudflare/Firewalls
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
                # Si viene empaquetado en un diccionario, buscamos la lista interna
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
                
        except requests.exceptions.RequestException as e:
            print(f"Error al conectar con {url}: {e}")
        except json.JSONDecodeError:
            print(f"Error al procesar el formato JSON de {url}.")
        except Exception as e:
            print(f"Ocurrió un error inesperado con {url}: {e}")

    # Forzamos la salida en formato JSON local estándar
    archivo_salida = "eventos_organizados.json"
    try:
        with open(archivo_salida, "w", encoding="utf-8") as f:
            # ensure_ascii=False guarda caracteres nativos como tildes
            json.dump(eventos_consolidados, f, indent=4, ensure_ascii=False)
        print(f"\n¡Completado con éxito! Se guardaron {len(eventos_consolidados)} eventos.")
    except IOError as e:
        print(f"Error al escribir el archivo de salida: {e}")

if __name__ == "__main__":
    extraer_y_organizar_eventos()

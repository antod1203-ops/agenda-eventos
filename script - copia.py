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
        
    # Si no es fútbol, mantiene su nombre original (con la primera letra en mayúscula o como venga)
    return str(category).strip()

def extraer_y_organizar_eventos():
    urls = [
        "https://la14hd.com/eventos/json/agenda123.json",
        "https://streamtp-abc.net/eventos.json"
    ]
    
    eventos_consolidados = []
    
    # User-Agent para simular una petición desde el navegador y evitar bloqueos
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    for url in urls:
        try:
            print(f"Conectando a: {url}...")
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            # Parsear la respuesta JSON
            data = response.json()
            
            # Detectar si el JSON viene como lista directa o dentro de un diccionario
            eventos_lista = []
            if isinstance(data, list):
                eventos_lista = data
            elif isinstance(data, dict):
                # Si es un diccionario, busca la primera lista interna (ej: data['eventos'])
                for clave, valor in data.items():
                    if isinstance(valor, list):
                        eventos_lista = valor
                        break
                if not eventos_lista:
                    eventos_lista = [data] # Si no hay listas, procesa el diccionario como único elemento
            
            # Mapear y formatear cada evento de la lista
            for item in eventos_lista:
                # Se usan alternativas comunes en las claves por si cambian de un origen a otro
                title = item.get("title") or item.get("nombre") or item.get("evento") or ""
                time = item.get("time") or item.get("hora") or item.get("inicio") or ""
                category = item.get("category") or item.get("categoria") or item.get("deporte") or ""
                status = item.get("status") or item.get("estado") or ""
                link = item.get("link") or item.get("url") or item.get("stream") or ""
                language = item.get("language") or item.get("idioma") or ""
                
                # Agrupar todo lo relacionado con fútbol en "Futbol"
                category_limpia = limpiar_categoria(category)
                
                # Estructura exacta solicitada
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

    # Guardar los datos organizados en un archivo JSON local
    archivo_salida = "eventos_organizados.txt"
    try:
        with open(archivo_salida, "w", encoding="utf-8") as f:
            # ensure_ascii=False guarda caracteres como tildes y eñes de forma nativa.
            json.dump(eventos_consolidados, f, indent=4, ensure_ascii=False)
        print(f"\n¡Completado con éxito! Se guardaron {len(eventos_consolidados)} eventos en '{archivo_salida}'.")
    except IOError as e:
        print(f"Error al escribir el archivo de salida: {e}")

if __name__ == "__main__":
    extraer_y_organizar_eventos()
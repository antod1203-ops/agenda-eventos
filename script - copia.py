name: Actualizador de Eventos para Blogger

on:
  schedule:
    - cron: '*/30 * * * *'
  workflow_dispatch:

permissions:
  contents: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - name: Clonar repositorio
      uses: actions/checkout@v4 # Esto elimina la advertencia de checkout

    - name: Configurar Python
      uses: actions/setup-python@v5 # Esto elimina la advertencia de python
      with:
        python-version: '3.10'

    - name: Instalar librerías necesarias
      run: pip install requests

    - name: Ejecutar script extractor
      run: python "script - copia.py"

    - name: Guardar cambios y subirlos a GitHub
      run: |
        git config --global user.name 'Blogger Bot'
        git config --global user.email 'bot@github.com'
        
        if [ -f "eventos_organizados.json" ]; then
          git add eventos_organizados.json
          git commit -m "Eventos actualizados automáticamente" && git push || echo "No hay cambios nuevos"
        elif [ -f "eventos_organizados.txt" ]; then
          git add eventos_organizados.txt
          git commit -m "Eventos actualizados automáticamente (.txt)" && git push || echo "No hay cambios nuevos"
        else
          echo "ERROR: El script no generó ningún archivo de salida. Revisa las conexiones del script."
          exit 1
        fi

import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests
import json

# Función para scrapear los candidatos desde el sitio web
def scrapear_candidatos(url):

    # Realizar la solicitud HTTP al sitio web
    response = requests.get(url)

    # Verificar si la solicitud fue exitosa (estado 200)
    if response.status_code == 200:
        
        # Obtener el contenido HTML de la página
        fuente_html = response.text

        # Utilizar expresiones regulares para extraer los nombres de los candidatos
        patron = r'\{\\"nombres\\".*?\\"candidateSlug\\":\\".*?\\"\}'
        candidatos_raw = re.findall(patron, fuente_html, re.DOTALL)

        # Para verificar cuántos bloques de candidatos se han encontrado
        print(f"Bloques encontrados: {len(candidatos_raw)}")

        # Lista de candidatos procesados con sus datos extraídos
        candidatos_procesados = []

        for candidato in candidatos_raw:
            try:

                # Limpiar el bloque de texto del candidato para que sea un JSON válido
                candidato_limpio = candidato.encode().decode('unicode_escape').encode('latin-1').decode('utf-8')

                # Convertir el candidato JSON a un diccionario de Python
                candidato = json.loads(candidato_limpio)

                # Extraer solamente la información relevante del candidato para este proyecto en concreto
                info_relevante = {
                        "nombre": f"{candidato.get('nombres')} {candidato.get('apellido_1', '')}",
                        "partido": candidato.get('partido_coalicion_o_movimiento'),
                        "lios": candidato.get('lios_yo_cuestionamientos')
                }
                candidatos_procesados.append(info_relevante)

            except json.JSONDecodeError:
                print(f"Error al decodificar el candidato: {candidato[:50]}...")  # Para verificar qué bloque de candidato causó el error
                continue # Continuar con el siguiente candidato en caso de error

        print(f"Candidatos procesados: {len(candidatos_procesados)}")  # Para verificar cuántos candidatos se han procesado
        return candidatos_procesados
    
    # En caso de que haya un error en la solicitud HTTP, se imprime el código de estado
    else:
        print(f"Error al acceder a la página: {response.status_code}")
    
# Función para graficar la cantidad de candidatos con líos o cuestionamientos por partido
def graficar_lios(candidatos):
    # Convertir la lista de candidatos a un DataFrame
    df = pd.DataFrame(candidatos)
    print(df['lios'].value_counts())

    # Considerar cualquier valor distinto a "No tiene" y "Sin datos" como "Tiene líos"
    df['tiene_lios'] = ~df['lios'].isin(['No tiene', 'Sin datos', ''])
    df_lios = df[df['tiene_lios']]

    # Separar partidos por coma y expandir cada uno en su propia fila
    df_partidos = df_lios.copy()
    df_partidos['partido'] = df_partidos['partido'].str.split(',')
    df_partidos = df_partidos.explode('partido')

    # Limpiar espacios en blanco que quedan después de separar
    df_partidos['partido'] = df_partidos['partido'].str.strip()

    # Contar la cantidad de candidatos con líos por partido
    conteo = df_partidos.groupby('partido').size().sort_values(ascending=False)

    # Estilo general
    sns.set_theme(style="whitegrid", palette="viridis")

    # Preparar datos para la gráfica
    conteo_df = conteo.reset_index()
    conteo_df.columns = ['partido', 'cantidad']

    # Crear figura
    fig, ax = plt.subplots(figsize=(14, 7))

    # Gráfica de barras horizontales
    sns.barplot(
        data=conteo_df,
        y='partido',       # Horizontal: partidos en el eje Y
        x='cantidad',      # Cantidad en el eje X
        palette='flare',   # Paleta de colores
        ax=ax
    )

    # Agregar el número al final de cada barra
    for container in ax.containers:
        ax.bar_label(container, padding=4, fontsize=10)

    # Títulos y etiquetas
    ax.set_title('Candidatos con líos o cuestionamientos por partido\nElecciones Congreso 2026', 
                fontsize=15, fontweight='bold', pad=20)
    ax.set_xlabel('Cantidad de candidatos con líos', fontsize=11)
    ax.set_ylabel('')

    # Quitar bordes innecesarios
    sns.despine(left=True, bottom=False)

    plt.tight_layout()
    plt.savefig('lios_por_partido.png', dpi=200, bbox_inches='tight')
    plt.show()

# URL del sitio web a scrapear
url = "https://elecciones-2026.lasillavacia.com"

candidatos = scrapear_candidatos(url)
graficar_lios(candidatos)
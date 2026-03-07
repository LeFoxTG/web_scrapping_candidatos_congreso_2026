import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests
import json

# Función para scrapear los candidatos desde el sitio web de la Silla Vacía y extraer la información relevante sobre candidatos con líos o cuestionamientos
def scrapear_candidatos(url):

    # Realizar la solicitud HTTP al sitio web
    response = requests.get(url)

    # Verificar si la solicitud fue exitosa (estado 200)
    if response.status_code == 200:
        
        # Obtener el contenido HTML de la página
        fuente_html = response.text

        # Utilizar una expresión regular para extraer los nombres de los candidatos
        # El patrón busca bloques de texto que contengan la estructura JSON con los datos de los candidatos, incluyendo el campo "nombres" y "candidateSlug"
        patron = r'\{\\"nombres\\".*?\\"candidateSlug\\":\\".*?\\"\}'
        candidatos_raw = re.findall(patron, fuente_html, re.DOTALL)

        # Para verificar cuántos bloques de candidatos se han encontrado
        print(f"Bloques encontrados: {len(candidatos_raw)}")

        # Lista de candidatos procesados con sus datos extraídos
        candidatos_procesados = []

        for candidato in candidatos_raw:
            try:

                # Limpiar el bloque de texto del candidato para que sea un JSON válido
                # El bloque de texto tiene caracteres de escape (\\) que deben ser procesados correctamente para convertirlo en un JSON válido
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
# Esta función toma la lista de candidatos procesados, filtra aquellos que tienen líos o cuestionamientos, y luego crea una gráfica de barras horizontales para mostrar la cantidad de candidatos con líos por partido.
def graficar_lios(candidatos):
    
    # Convertir la lista de candidatos a un DataFrame
    # Esto facilita el análisis y la manipulación de los datos, permitiendo filtrar y agrupar fácilmente por partido.
    df = pd.DataFrame(candidatos)
    print(df['lios'].value_counts())

    # Considerar cualquier valor distinto a "No tiene" y "Sin datos" como "Tiene líos"
    df['tiene_lios'] = ~df['lios'].isin(['No tiene', 'Sin datos', ''])
    df_lios = df[df['tiene_lios']]

    # Separar partidos por coma y expandir cada uno en su propia fila
    # Esto es necesario porque algunos candidatos pueden estar asociados a múltiples partidos o movimientos, y queremos contar cada partido por separado.
    df_partidos = df_lios.copy()
    df_partidos['partido'] = df_partidos['partido'].str.split(',')
    df_partidos = df_partidos.explode('partido')

    # Limpiar espacios en blanco que quedan después de separar
    df_partidos['partido'] = df_partidos['partido'].str.strip()

    # Contar la cantidad de candidatos con líos por partido
    conteo = df_partidos.groupby('partido').size().sort_values(ascending=False)

    # Configurar el estilo de la gráfica para que sea más pro :p
    dark_params = {
            "figure.facecolor": "#121212",  # Fondo de la ventana/imagen
            "axes.facecolor": "#121212",    # Fondo del área de la gráfica
            "text.color": "#E0E0E0",        # Color del texto de títulos
            "axes.labelcolor": "#E0E0E0",   # Color del texto de los ejes
            "xtick.color": "#A0A0A0",       # Color de los valores en X
            "ytick.color": "#E0E0E0",       # Color de los nombres de los partidos en Y
            "grid.color": "#2A2A2A",        # Color de las líneas guía (sutil)
            "axes.edgecolor": "#2A2A2A"     # Color del borde de la gráfica
        }

    # Estilo general
    # Se utiliza el estilo "darkgrid" de Seaborn para agregar un fondo oscuro con líneas guía, y se aplican los parámetros personalizados que se definieron.
    sns.set_theme(style="darkgrid", rc=dark_params)

    # Preparar datos para la gráfica
    # El conteo de candidatos con líos por partido se convierte en un DataFrame para facilitar la creación de la gráfica, y se renombrar las columnas para que sean más descriptivas.
    conteo_df = conteo.reset_index()
    conteo_df.columns = ['partido', 'cantidad']

    # Crear figura
    fig, ax = plt.subplots(figsize=(14, 7))

    # Gráfica de barras horizontales
    sns.barplot(
        data=conteo_df,
        y='partido',       # Horizontal: partidos en el eje Y
        x='cantidad',      # Vertical: cantidad de candidatos con líos en el eje X
        hue='partido',     # Diferenciar por partido usando el mismo campo para el color
        palette='viridis', # Paleta de colores
        ax=ax
    )

    # Agregar el número al final de cada barra
    for container in ax.containers:
        ax.bar_label(container, padding=4, fontsize=10, color="#E0E0E0")

    # Títulos y etiquetas
    ax.set_title('Candidatos con líos o cuestionamientos por partido\nElecciones Congreso 2026', 
                fontsize=15, fontweight='bold', pad=20)
    ax.set_xlabel('Cantidad de candidatos con líos', fontsize=11)
    ax.set_ylabel('')

    # Quitar bordes innecesarios
    # Se eliminan los bordes izquierdo y superior para un diseño más limpio, mientras que el borde inferior se mantiene para enmarcar la gráfica.
    sns.despine(left=True, bottom=False)

    plt.tight_layout()
    plt.savefig('lios_por_partido.png', dpi=200, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.show()
    
    return conteo_df

# Función para comparar los datos extraídos de la Silla Vacía con los datos del informe de la Fundación Pares
# Esta función toma el conteo de candidatos con líos por partido obtenido del scraping, crea un DataFrame con los datos del informe de la Fundación Pares, y luego combina ambos conjuntos de datos para crear una gráfica de barras agrupadas que muestra la comparación entre las dos fuentes.
# En el caso de Pares, no hizo falta realizar Web Scraping porque el informe ya estaba disponible en formato PDF, y se pudo extraer la información manualmente para crear el DataFrame correspondiente.
# https://www.pares.com.co/wp-content/uploads/2026/02/INFORME-de-candidatos-cuestionados-1.pdf
def comparativa_con_pares(conteo_df_datos_silla):

    # Añadir etiqueta de fuente a los datos extraidos de La Silla Vacía
    # Esto es importante para poder diferenciar en la gráfica de barras agrupadas entre los datos que provienen del scraping y los datos que provienen del informe de la Fundación Pares, ya que ambos conjuntos de datos se combinarán en un solo DataFrame para la visualización.
    df_datos_silla = conteo_df_datos_silla.copy()
    df_datos_silla['Fuente'] = 'La Silla Vacía'

    #Crear DataFrame con los datos extraídos del informe de Pares
    datos_pares = {
        'partido': [
            'Partido Liberal', 
            'Partido Conservador', 
            'Partido de La U', 
            'Cambio Radical',
            'Centro Democrático',
            'Mira',
            'La Fuerza',
            'Mais',
            'ADA',
            'Esperanza Democrática',
            'Partido del Trabajo',
            'Partido Ecologista',
            'Alianza Verde',
            'Colombia Justa Libres',
            'Pacto Histórico',
            'Liga Anticorrupción',
            'Colombia Renaciente',
            'Dignidad',
            'ASI',
            'En Marcha',
            'Nuevo Liberalismo',
            'Salvación Nacional',
            'Dignidad y Compromiso',
            'Partido Demócrata Colombiano',
            'Partido Verde Oxigeno',
            'Comunes',
            'Fuerza Ciudadana'
        ],
        'cantidad': [33, 32, 29, 24, 18, 15, 14, 13, 11, 11, 11, 11, 11, 10, 10, 10, 9, 9, 8, 7, 7, 6, 5, 5, 2, 1, 1]
    }
    df_pares = pd.DataFrame(datos_pares)
    df_pares['Fuente'] = 'Fundación Pares'

    # Unir ambos DataFrames para la gráfica de barras agrupadas
    df_combinado = pd.concat([df_datos_silla, df_pares])

    # Configurar el estilo de la gráfica para que sea más pro 2.0 :p
    dark_params = {
        "figure.facecolor": "#121212",
        "axes.facecolor": "#121212",
        "text.color": "#E0E0E0",
        "axes.labelcolor": "#E0E0E0",
        "xtick.color": "#A0A0A0",
        "ytick.color": "#E0E0E0",
        "grid.color": "#2A2A2A",
        "axes.edgecolor": "#2A2A2A"
    }
    sns.set_theme(style="darkgrid", rc=dark_params)

    # Calcular el valor máximo entre las dos fuentes para cada partido
    # Esto es necesario para ordenar los partidos en la gráfica de barras agrupadas de manera que se muestren en el mismo orden en ambas fuentes, basándose en el valor máximo de candidatos con líos reportados por cualquiera de las dos fuentes.
    orden_partidos = df_combinado.groupby('partido')['cantidad'].max().sort_values(ascending=False).index

    # Crear figura más ancha para acomodar barras dobles
    fig, ax = plt.subplots(figsize=(14, 12))

    # Gráfica de barras agrupadas usando 'hue' para diferenciar entre las dos fuentes de datos
    sns.barplot(
        data=df_combinado,
        y='partido',
        x='cantidad',
        hue='Fuente',        # Esto separa las barras por el origen de los datos
        order= orden_partidos,  # Ordenar los partidos según el valor máximo de candidatos con líos
        palette=["#00a2ff", "#00ff62"], # Colores personalizados para cada fuente
        ax=ax
    )

    # Agregar el número al final de cada barra
    for container in ax.containers:
        ax.bar_label(container, padding=4, fontsize=10, color="#E0E0E0")

    # Títulos y etiquetas
    ax.set_title('Comparativo: Candidatos con líos por partido\nMis Datos vs. Fundación Pares (Elecciones 2026)', 
                 fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Cantidad de candidatos con líos', fontsize=12)
    ax.set_ylabel('')

    # Ajustar la leyenda para el modo oscuro
    legend = ax.legend(title='Fuente de Datos', facecolor='#121212', edgecolor='#2A2A2A')
    plt.setp(legend.get_texts(), color='#E0E0E0')
    plt.setp(legend.get_title(), color='#E0E0E0')

    # Quitar bordes innecesarios y mantener el borde inferior para enmarcar la gráfica
    sns.despine(left=True, bottom=True)

    plt.tight_layout()
    plt.savefig('comparativo_lios_partidos.png', dpi=200, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.show()

# URL del sitio web a scrapear
url = "https://elecciones-2026.lasillavacia.com"

candidatos = scrapear_candidatos(url)
conteo_silla = graficar_lios(candidatos)
comparativa_con_pares(conteo_silla)

#
#                    ▒▒░░                             ░▒▒▓▓▓▓▓▓▒                                     
#                    ▒▓▓▒▒░                          ░▒▓▓▓▓▓▓▓▓▒░                                    
#                    ▒▓▓▓▓▓▒▒░          ░░░░░░░░░░░ ▒▒▓▓▓▓▓▓▓▓▓▓░                                    
#                    ░▓▓▓▓▓▓▓▓▒▒    ░░░░▒░░▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓▓▓▒░                                   
#                    ░▒▓▓▓▓▓▓▓▓▒▒░░░░░░▒░░░▒▒▒▒▒▒▒▒▒░▒▒▒▒░░▒▒▒▒▒▒░                                   
#                    ░▒▓▓▓▓▓▓▒▒▒░░░░░░░░░░░░░░░░░░▒▒▒░░░░░░░░░░░░░░                                  
#                    ░▒▓▓▓▒▒▒░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░                                  
#                     ▒▓▒▒░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░                                 
#                     ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░                                
#                     ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░                                
#                     ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░                               
#                     ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░                              
#                     ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░                              
#                     ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░                             
#                     ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░                            
#                     ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░                            
#                     ▒░░░▒▒▒▒░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▒▒                           
#                     ▒░░▒▒▒▒▒▒░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▒▒▒▒▒░                          
#                     ▒░░▒▒▒▒▒░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  ░▒▒▒▒▒▒                          
#                     ▒░░▒▒▒▒░░░░░░░░░░░░░░░░░░░░░░░░░░░         ░░░░▒▒▒▒▒▒▒                         
#                     ▒▒░▒▒░░░░░░░░░░░░░░░░░░░░░░░░░    ░░░░░░░░░░░░▒▒▒▒▒▒▒▒▒▒▒▒░                    
#                     ░░░░░░░░░░        ░░▒▒▒▒▒░░░░░░░░░░░░░▒▒▒▒▒▒▒░░▒▒▒▒█▒▒▒▒▒▒▒▒▒▒░                
#                     ░               ░░░░░░░░░▒▒▒▒▒▒▒▒▒░▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒█▒▒▒▒▒▒▒▒▒▓▓▓▓▒░            
#                        ░░░░░░░░░░░░░░▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓▒▒▒▒▒░▒▒▒▒▒▒▒▒▓▓▓▓▓▓▓░           
#                   ░▒▒▒░░░ ░░▒▒▒▒▒▒▒▒▒░▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓░░░▒░░░░░░░░░░░░░▒▒▒▒▒▒▓▓▓▓▓▓▓▒             
#                ░▒▒▒▒▒▒▒░ ░░▒░░░▒▒▒▒▒▒▒▒▒▒▒▒▓▒░░░░░░░░░▒▓▓▒░░░░░░░░░░░░░▒▒▒▒▒▒▓▓▓▓▓▓▒░              
#             ░░▒▓▒▒▒▒▒██▒░░░░░▒░░▒▒  ░░  ░      ░▓██▒░░▒███▒▓▓░░░░░░░░░▒▒▒▒▒▒▒▒▒▒▒▒░                
#           ░▒▓▓▓▓▒▒░░▒▒░  ░  ░░░░            ▒▒▒▒▒▓▓▓███▒░░███▓▒▒▒░░░▒▒▒▒▒▒▒▒▒▒▒▒░                  
#           ░▒▓▓▓▓▓▓▒   ▓▓█░  ▓██▓░░░         ▒▒▒▒▒░░░▓█▓▓██▓░░▒███▒▒▒▒▒▒▒▒▒▒▒▒▒░                    
#              ░▓▓▓▓▒   ▓██▓▓▓▓▒▒░███░░░░  ░▒▒▒▒▒▒▒▒▒░░░░▒██▓░░░▒▒░░▒▒▒▒▒▒▒▒▒▒▒                      
#                ░░▒▒░░░   ▒███▒▓█▓▒▒▓██▓   ▒▒▒▒▒▒▒▒▒▒▒▒▒░░░░▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒                        
#                   ░░░▒░░░ ░░░▓██▓  ░▓▒░░▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒░                          
#                      ░░▒▒░░░  ░░░   ░░░▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒                            
#                        ░░▒▒▒░▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓▓▒▒▒▒▒▒▒▒▒▒▒▒▒░                            
#                           ░▒▒▒▒▒▒▒▒▒▒▒▒▓▒▒▒▒▒▒▒ ░▒▒▓▓▓▓▓▓▒▒▒▒▒▒▒▒▒▒▒▒▒       ░▒▒░                  
#                             ░▒▒▒▒▒▒▒▒▒▒▓▓▓▓▓▓▓▒  ▒▓▓▓▓▓▓▓▓▒▒▒▒▒▒▒▒▒▒▒░     ░▒▒▒▒▒░                 
#                               ▒▒▒▒▒▒▒▒▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒▒▒▒▒▒▒▒▒▒░   ░▒▒▒▒▒▒▒▒░                
#                               ░▒▒▒▒▒▒▒▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒▒▒▒▒▒▒▒░    ░▒▒▒▒▒▒▓▒▒▒░               
#                                ▒▒▒▒▒▒▒▒▒▒▓██▓▓▓█▓▓▓▓▓▓▓▓▓▓▓▒▒▒▒░          ▒▒▓▓▒▒▒▒▒▒░              
#                                 ▒▒▒▒▒▒▒▒▒▓██▓█▓▓▓▓▓▓▓▓▓▓▓▓▒▒░              ▒▒▒▒▒▓▓▓▓▒▒             
#                                   ░░░░▒▒▒▒▓▓▓▓▓▓▓█▓▓▓▓▒▒▒▓▒▓▒░░            ░▒▒▓▓▓▓▓▓▓▓░            
#                       ░░░░░░░░░░░░░░░░░░▒▒▓▒▒▓█▓▓▓▓▓▓▓▒▓▓▒▒▓▒░░░░░         ░▒▓▒▓▓▓▓▓▓▒▒░           
#                      ░░░░░░░░░░░░░░░░░░▒▓▓▒▓▓▓▓▓▓▓▓▓▓▒▓▓▓▓▓▒▒░░░░░░░░░      ░▒▓▒▓▓▓▒▒▓▓▓▒░         
#                     ░░░░░░░░░░░░░░░░░░░▓▓▓▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒░░░░░░░░░░░░░     ▒▓▓▓▓▓▓▓▓▓▓▒         
#                    ░░░░░░░░░░░░░░░░░░░▒▓▓▓▓█▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒░░░░░░░░░░░░░░░░░   ░▓▓▓▓▓▒▒▒░░░        
#                    ░░░░░░░░░░░░░░░░░░░▒▓▓▓███▓▓▓▓▓▓▓▓▓▓▓▒▒░░░░░░░░░░░░░░░░░░░   ░▒▒░░░░░░░░░       
#                   ░░░░░░░░░░░░░░░░░░░░▒▓▓████▓▓▓▓█▓▓▓▓▓▒░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░      
#                  ░░░░░░░░░░░░░░░░░░░░▒▓▓▓████▓▓████▓▓▒░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   ░▒
#                 ░░░░░░░░░░░░░░░░░░░░▒▓▓▓███████████▒▒░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▒▒▒▒▒
#                ░░░░░░░░░░░░░░░░░░░░░▒▓▓███████████▓▓▒░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▒▒▒▒
#               ░░░░░░░░░░░░░░░░░░░░░░▓▓▓███████████▓▒▒░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▒▒▒
#              ░░░░░░░░░░░░░░░░░░░░░░▒▓▓███████████▓▓▒░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▒▒
#              ░░░░░░░░░░░░░░░░░░░░░░▒▓▓███████████▓▒▒░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▒
#             ░░░░░░░░░░░░░░░░░░░░░░░▒▓▓███████████▓▒▒░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
#            ░░░░░░░░░░░░░░░░░░░░░░░░▒▓████████████▓▒░░░░░░░░░░░░░░░░░░░░░░▒▒▒░░░░░░░░░░░░░░░░░░░░░░░
# FoxTG 🗣💕

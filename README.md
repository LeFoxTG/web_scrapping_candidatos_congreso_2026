# Web Scrapping candidatos al congreso 2026
Web Scrapping sencillo hecho con python para extraer los datos de los candidatos al Congreso de la República de Colombia para el año 2026, tomados del medio de comunicación [La Silla Vacía](https://elecciones-2026.lasillavacia.com).
Los candidatos se agrupan por partido y el programa permite visualizar en una gráfica de barras la cantidad de candidatos con líos o cuestionamientos en cada partido.

### **Actualización!!!1!!11!**
Ahora, además del scrapping, se añadieron los datos de un informe de la [Fundación Pares](https://www.pares.com.co/elecciones-colombia-2026/candidatas-y-candidatos-cuestionados-al-congreso-de-la-republica-2026/), en el cual también se enlistan los candidatos con líos/cuestionamientos. Todos los datos de ambas fuentes se fusionan en la gráfica final para poder hacer una comparativa.

---

## Resultado obtenido
### Solo utilizando [La Silla Vacía](https://elecciones-2026.lasillavacia.com) como fuente
![Gráfica de líos por partido](https://i.ibb.co/qMG9vVWc/lios-por-partido.png")
### Utilizando y comparando ambas fuentes ([La Silla Vacía](https://elecciones-2026.lasillavacia.com) y [Fundación Pares](https://www.pares.com.co/elecciones-colombia-2026/candidatas-y-candidatos-cuestionados-al-congreso-de-la-republica-2026/))
![Gráfica de líos por partido (comparativa ambas fuentes)](https://i.ibb.co/3yRvkb4h/comparativo-lios-partidos.png")
---

## ¿Cómo funciona?
El sitio de La Silla Vacía está construido con **Next.js**, lo que significa que los datos no viven en el HTML tradicional sino embebidos en bloques de JavaScript (`self.__next_f.push`). El scraper:

1. Descarga el HTML completo de la página con `requests`
2. Usa **expresiones regulares** para localizar y extraer cada bloque JSON de candidato
3. Limpia las secuencias de escape del string JavaScript para convertirlo en JSON válido
4. Procesa y filtra la información relevante con **pandas**
5. Genera una gráfica con **seaborn** y **matplotlib**

Para la comparativa con los datos de la Fundación Pares, dado que estos datos ya estaban debidamente agrupados y contados en el informe anexo al artículo, se agregaron de forma manual sin necesidad de scrapping y se construyo una gráfica utilizando el Data Frame ya creado con anteriridad perteneciente a los datos de la Silla Vacía, y junto con el Data Frame de Pares, se unieron para hacer una gráfica de doble barra para cada partido utilizando **seaborn** y **matplotlib**. Un detalle importante es la revisión rigurosa del nombre de los partidos, pues incluso la diferencia en una mayúscula hacía que el programa no interprete que son el mismo partido y los muestre como dos partidos distintos. Por ejemplo, en Pares el 'Partido Liberal' era referenciado como 'Partido Liberal Colombiano', así que tuvo que ser renombrado a ser solo 'Partido Liberal' para que coincidiera con el nombre dado en la Silla Vacía y el programa pudiera interpretar que son el mismo grupo y comparar las cantidades de candidatos cuestionados.

---

## Instalación

**1. Clona el repositorio**
```bash
git clone https://github.com/LeFoxTG/web_scrapping_candidatos_congreso_2026
```

**2. Instala las dependencias**
```bash
pip install requests pandas matplotlib seaborn
```

---

## Uso

```bash
python scrapping.py
```

Al ejecutarlo verás en consola:
```
Bloques encontrados: 618
Candidatos procesados: 618
```

Y se generará automáticamente el archivo `lios_por_partido.png` en la misma carpeta.
De igual manera se generará `comparativo_lios_partidos.png` para la gráfica comparativa.

---

## Datos extraídos por candidato

| Campo | Descripción |
|---|---|
| `nombre` | Nombre y primer apellido |
| `partido` | Partido o coalición |
| `lios` | Categoría de líos o cuestionamientos |

Los posibles valores del campo `lios` son:

- `No tiene`
- `Tiene apoyo cuestionado`
- `Tiene imputación penal`
- `Tiene sanción disciplinaria/fiscal`
- `Condena de primera instancia`
- `Sin datos`

En este caso el criterio para decidir que candidatos tienen líos o cuestionamientos es seleccionar a todos aquellos que en ese campo tienen un valor distinto a "No tiene" o "Sin datos".

---

## Decisiones técnicas

**¿Por qué regex y no BeautifulSoup?**
Los datos no están en etiquetas HTML sino dentro de strings JavaScript. BeautifulSoup no puede parsear el contenido de esos scripts, pero una expresión regular sí puede localizar cada bloque `{\"nombres\":...\"candidateSlug\":...}` directamente.

**¿Por qué `encode().decode('unicode_escape').encode('latin-1').decode('utf-8')`?**
Los strings JavaScript tienen múltiples niveles de escape (`\\\\\\"` para representar una comilla dentro de un valor). Esta cadena de transformaciones los resuelve todos en orden sin romper los caracteres especiales del español como `ó`, `é`, `ñ`.

**¿Por qué `explode()` en pandas?**
Algunos candidatos pertenecen a coaliciones con varios partidos separados por coma. Con `str.split(',')` + `explode()` cada partido de la coalición cuenta por separado en la gráfica, evitando que las coaliciones opaquen a los partidos individuales.

**¿Por qué no se utilizó Web Scrapping para los datos de la Fundación Pares?**
Para el caso de la Fundación Pares, en su artículo respecto a los candidatos cuestinados que ellos documentaron, anexaron un [informe](https://www.pares.com.co/wp-content/uploads/2026/02/INFORME-de-candidatos-cuestionados-1.pdf) en el cual ya realizaban la labor de contar el número total de señalados por líos/cuestionamientos y agruparlos por partido, incluso añadiendo una gráfica similar a la realizada en este proyecto para la Silla Vacía. De tal forma que para esta fuente solo hizo falta copiar los datos manualmente para el Data Set en lugar de Scrappearlos de forma automatizada.

---

Hecho con ❤️ por FoxTG

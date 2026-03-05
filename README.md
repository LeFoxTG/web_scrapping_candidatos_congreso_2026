# Web Scrapping candidatos al congreso 2026
Web Scrapping sencillo hecho con python para extraer los datos de los candidatos al Congreso de la República de Colombia para el año 2026, tomados del medio de comunicación [La Silla Vacía](https://elecciones-2026.lasillavacia.com).
Los candidatos se agrupan por partido y el programa permite visualizar en una gráfica de barras la cantidad de candidatos con líos o cuestionamientos en cada partido.

---

## Resultado obtenido
![Gráfica de líos por partido](https://i.ibb.co/7Nnf27hg/lios-por-partido.png")

---

## ¿Cómo funciona?
El sitio de La Silla Vacía está construido con **Next.js**, lo que significa que los datos no viven en el HTML tradicional sino embebidos en bloques de JavaScript (`self.__next_f.push`). El scraper:

1. Descarga el HTML completo de la página con `requests`
2. Usa **expresiones regulares** para localizar y extraer cada bloque JSON de candidato
3. Limpia las secuencias de escape del string JavaScript para convertirlo en JSON válido
4. Procesa y filtra la información relevante con **pandas**
5. Genera una gráfica con **seaborn** y **matplotlib**

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
python scraper.py
```

Al ejecutarlo verás en consola:
```
Bloques encontrados: 573
Candidatos procesados: 573
```

Y se generará automáticamente el archivo `lios_por_partido.png` en la misma carpeta.

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

---

Hecho con ❤️ por FoxTG

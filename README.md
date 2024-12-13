# 🏡 Reffindr Python Data Repository

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)  
[![Flask](https://img.shields.io/badge/Flask-v2.0.3-orange)](https://flask.palletsprojects.com/)  
[![AWS RDS](https://img.shields.io/badge/AWS-RDS-green)](https://aws.amazon.com/rds/)  
[![Status](https://img.shields.io/badge/status-active-success.svg)](https://github.com/tu_usuario/reffindr-python-data)

Este repositorio contiene los scripts y recursos creados por el equipo **Python Data** para el proyecto **Reffindr**, enfocándose en la extracción, transformación y carga (ETL) de datos inmobiliarios, así como la creación de una API REST con Flask.

---

## 🌟 Funcionalidades Principales

- **Web scraping con Flask API**: Extrae datos de propiedades inmobiliarias desde [Argenprop](https://www.argenprop.com/).
- **ETL automatizado**: Procesa los datos extraídos, los transforma y los carga en una base de datos AWS RDS.
- **Modelo de datos**: Estructura optimizada y documentada en un diagrama de relación (ER Diagram).

---

## 📂 Estructura del Proyecto

```plaintext
reffindr-python-data/
├── app.py                   # API desarrollada con Flask para scraping
├── etl.py                   # Pipeline ETL: extracción, transformación y carga
├── functions/               # Funciones auxiliares reutilizables
├── scrapper/                # Código específico para scraping
├── static/                  # Archivos estáticos para entornos staging/producción
├── Data_ficticia/           # Datos ficticios para pruebas locales
├── Dockerfile               # Configuración de Docker para contenedores
├── requirements.txt         # Dependencias necesarias para ejecutar el proyecto
├── ERD DIAGRAM REFFINDR TEAM DATA.pdf  # Modelo de base de datos
├── README.md                # Este archivo
└── compose.yaml             # Configuración de Docker Compose
```
---

## 🚀 Cómo Empezar

### 1️⃣ Clonar el Repositorio
Primero, clona este repositorio en tu máquina local:

```bash
git clone https://github.com/igrowker/i004-reffindr-back-python.git
cd reffindr-python-data
```
---

### 2️⃣ Configurar Variables de Entorno
#### 🛠️ Configuración de Base de Datos

El proyecto utiliza una base de datos alojada en **AWS RDS** como ejemplo, pero puedes configurar tu propia base de datos con tus credenciales. Para esto, asegúrate de definir las siguientes variables en un archivo `.env`:

```plaintext
DB_USER=tu_usuario        # Usuario de la base de datos
DB_PASSWORD=tu_contraseña # Contraseña de la base de datos
DB_HOST=tu_host           # Dirección del host (ejemplo: localhost o una URL de RDS)
DB_NAME=tu_basededatos    # Nombre de tu base de datos
DB_SCHEMA=tu_esquema      # Nombre del esquema (opcional)
```

### 3️⃣ Instalar Dependencias
Asegúrate de tener Python 3.9+ instalado. Luego, ejecuta:

```plaintext
pip install -r requirements.txt
```

## 🖥️ Uso de la API (app.py)
Ejecutar la API Localmente
Inicia el servidor Flask localmente con:

```plaintext
python app.py
```

## Endpoints Disponibles

Este proyecto expone los siguientes endpoints para interactuar con la API:

### `/swagger`
- **Método:** `GET`
- **Descripción:** Proporciona documentación interactiva generada automáticamente con [Swagger](https://swagger.io/) para explorar y probar la API.

### `/argenprop`
- **Método:** `GET`
- **Descripción:** Realiza scraping de propiedades en Argenprop basadas en los parámetros proporcionados.
- **Parámetros:**
  - `pais`: Especifica el país de las propiedades a obtener (por ejemplo, "argentina").
  - `limite`: Establece el número máximo de propiedades a obtener (por ejemplo, "10").
  
- **Ejemplo de solicitud:**
http://127.0.0.1:5000/argenprop?pais=argentina&limite=10


## 🗂️ Modelo de Base de Datos
El archivo ERD DIAGRAM REFFINDR TEAM DATA.pdf contiene el diseño del modelo relacional, incluyendo las tablas principales para almacenar datos de propiedades, usuarios y agentes inmobiliarios.

---

## 🛠️ Tecnologías Utilizadas

- **Lenguaje:** Python
- **Framework API:** Flask
- **Base de Datos:** AWS RDS

## Librerías Clave

- **Flask**: Creación de la API.
- **BeautifulSoup**: Scraping de datos HTML.
- **pandas**: Manipulación de datos.
- **sqlalchemy**: Conexión a bases de datos.
- **boto3**: Interacción con AWS.
- **argparse**: Manejo de argumentos para el script ETL.






#===============================================================================================
# Librerías
#===============================================================================================
import requests
import numpy as np
import pandas as pd
from datetime import datetime
import pytz
from unidecode import unidecode
import psycopg2
from sqlalchemy import create_engine

from functions.functions import convert_to_ars
from functions.functions import obtener_direccion
from functions.functions import extract_relevant_address
from functions.functions import extract_state
from functions.functions import assign_salary_range
from functions.functions import remove_last_two_parts

#===============================================================================================
# 1. EXTRACT
#===============================================================================================
url = 'https://i004-reffindr-back-python-dev.onrender.com/argenprop'
#url = 'http://reffindr-alb-1167121448.us-east-1.elb.amazonaws.com:41555/argenprop'

# Parámetros de la solicitud
params = {'pais': 'argentina', 'limite': 300}
response = requests.get(url, params=params)
data = response.json()
df = pd.DataFrame(data)

#===============================================================================================
# 2. TRANSFORMATIONS
#===============================================================================================

#===============================================================================================
## 2.1 TABLA STATES
#===============================================================================================
data_states = {
    1: "Buenos Aires",
    2: "Catamarca",
    3: "Chaco",
    4: "Chubut",
    5: "Córdoba",
    6: "Corrientes",
    7: "Entre Ríos",
    8: "Formosa",
    9: "Jujuy",
    10: "La Pampa",
    11: "La Rioja",
    12: "Mendoza",
    13: "Misiones",
    14: "Neuquén",
    15: "Río Negro",
    16: "Salta",
    17: "San Juan",
    18: "San Luis",
    19: "Santa Cruz",
    20: "Santa Fe",
    21: "Santiago del Estero",
    22: "Tierra del Fuego",
    23: "Tucumán",
    24: "Ciudad Autónoma de Buenos Aires",
}
States = pd.DataFrame(data_states.items(), columns=["Id", "StateName"])

#===============================================================================================
## 2.2 Transformación Tabla de datos de Propietarios
#===============================================================================================
df_properties = df.copy()

# Convertir precios a ARS
df_properties['Price'] = df_properties['Price'].apply(convert_to_ars)

# Reemplazar comas por puntos en las columnas 'Latitude' y 'Longitude'
df_properties['Latitude'] = df_properties['Latitude'].apply(lambda x: str(x).replace(',', '.') if isinstance(x, str) else str(x))
df_properties['Longitude'] = df_properties['Longitude'].apply(lambda x: str(x).replace(',', '.') if isinstance(x, str) else str(x))

# Convertir las columnas 'Latitude' y 'Longitude' a tipo float
df_properties['Latitude'] = pd.to_numeric(df_properties['Latitude'], errors='coerce')
df_properties['Longitude'] = pd.to_numeric(df_properties['Longitude'], errors='coerce')

# Identificar y eliminar filas con espacios vacíos en las columnas de tipo cadena
string_columns = df_properties.select_dtypes(include=['object', 'string'])
rows_with_spaces = string_columns.apply(lambda col: col.str.strip() == '', axis=0).any(axis=1)
df_properties = df_properties[~rows_with_spaces].reset_index(drop=True)

# Eliminar valores nulos (NaN)
df_properties = df_properties.dropna().reset_index(drop=True)

# Obtener dirección, provincia, pais
df_properties['Address'] = df_properties.apply(lambda x: obtener_direccion(x['Latitude'], x['Longitude']), axis=1)

df_properties.dropna(inplace=True)
df_properties.reset_index(drop=True, inplace=True)

# Crear una lista de estados válidos a partir de un DataFrame 'States'
states_list = States["StateName"].tolist()

# Obtener estado
df_properties["StateName"] = df_properties["Address"].apply(extract_relevant_address)
df_properties["StateName"] = df_properties["StateName"].apply(lambda x: extract_state(x, states_list))

#Limitar solo dirección 
df_properties['Address'] = df_properties['Address'].apply(lambda x: ', '.join(x.split(', ')[:3]))

#Eliminar columnas Latitud, Longitud
df_properties = df_properties.drop(columns=['Latitude', 'Longitude'])

df_properties.dropna(inplace=True) 
df_properties.reset_index(drop=True, inplace=True)

# Convertir img a formato string y eliminando filas ''
df_properties['img'] = df_properties['img'].astype(str)
df_properties.drop(df_properties[df_properties['img'] == '[]'].index, inplace=True)

df_properties.reset_index(drop=True, inplace=True)
df_properties.drop(df_properties[df_properties['Title'].str.contains('U\$', na=False)].index, inplace=True)

# Tomar una muestra aleatoria de 100 propiedades y resetear el índice
df_prop = df_properties.sample(n=100, random_state=100).reset_index(drop=True)

df_prop.insert(0, 'Id', range(1, len(df_prop) + 1))

# Definir las columnas adicionales a agregar al DataFrame con valores específicos
columnas = [
    "Water", "Gas", "Surveillance", "Electricity", "Internet", 
    "Pool", "Garage", "Pets", "Grill", "Elevator", "Terrace",
    "IsHistoric", "IsWorking", "HasWarranty", "RangeSalary"
]

# Agregar columnas con valores específicos
for column in columnas:
    if column in ["Water", "Gas", "Electricity"]:
        df_prop[column] = True  
    elif column in ["Surveillance", "Pets", "Pool"]:
        df_prop[column] = np.random.choice([True, False], size=len(df_prop))
    elif column == "RangeSalary":
        salary_range = np.random.triangular(left=400000, mode=900000, right=3000000, size=len(df_prop))
        salary_range = salary_range.astype(int) 
        df_prop[column] = salary_range
    else:
        df_prop[column] = np.random.choice([True, False], size=len(df_prop), p=[0.8, 0.2])

# Agregar la columna 'CreatedAt' con la fecha y hora actuales en formato UTC
df_prop.loc[:, 'CreatedAt'] = datetime.now(pytz.UTC)

# Crear la columna 'UpdatedAt' con valores nulos
df_prop['UpdatedAt'] = pd.Series([None] * len(df_prop), dtype="datetime64[ns]")

# Crear la columna 'IsDeleted' con valor por defecto 'False'
df_prop['IsDeleted'] = False

# Definir el orden de las columnas para el DataFrame final
orden_columns = [
    "Id","img","IsWorking", "HasWarranty", "RangeSalary", "CountryName", "StateName", "Title", "Address", "Price", "Environments", 
    "Bathrooms", "Bedrooms", "Seniority", "Water", "Gas", "Surveillance", "Electricity", "Internet", "Pool", 
    "Garage", "Pets", "Grill", "Elevator", "Terrace", "IsHistoric", "Description", "CreatedAt", "UpdatedAt",
    "IsDeleted"
]
df_prop = df_prop[orden_columns]

# Definir los rangos salariales
ranges = [
    (300000, 600000),
    (600000, 1000000),
    (1000000, 3000000),
    (3000000, float("inf"))
]

# Asignar los rangos salariales a la columna 'RangeSalary'
df_prop["RangeSalary"] = df_prop["RangeSalary"].apply(assign_salary_range)

#Cambiar de nombre a SalaryId
df_prop.rename(columns={'RangeSalary': 'SalaryId'}, inplace=True)

#Cambiar las columnas a tipo Int64
df_prop[['Environments', 'Bathrooms', 'Bedrooms', 'Seniority']] = df_prop[['Environments', 'Bathrooms', 'Bedrooms', 'Seniority']].astype('int64')

#===============================================================================================
## 2.3 Transformación Tabla de datos de Usuarios
#===============================================================================================
# Cargar el archivo CSV con la información de los usuarios ficticios
csv_path = 'Data_ficticia\\Users_Ficticios_IA.csv'
df_users = pd.read_csv(csv_path, delimiter=';')

# Tomar una muestra aleatoria de 200 usuarios y resetear el índice
df_users = df_users.sample(n=200, random_state=5).reset_index(drop=True)

# Limpieza, solo me quedo con la dirección
df_users['Address'] = df_users['Address'].apply(remove_last_two_parts)

#Insertación de nuevas columnas ficticias.
df_users.insert(0, 'Id', range(1, len(df_users) + 1))
df_users.insert(1, 'RoleName', ['Tenant' if i % 2 == 0 else 'Owner' for i in range(len(df_users))])
df_users.insert(2, 'CountryName', 'Argentina')
df_users.insert(4, 'IsCompany', df_users['RoleName'].apply(lambda x: 'False' if x == 'Owner' else ''))
df_users.insert(13, 'IsProfileComplete', 'True')
df_users.insert(15, 'CreatedAt', datetime.now(pytz.UTC))
df_users.insert(16, 'UpdatedAt', pd.Series([None] * len(df_users), dtype="datetime64[ns]"))
df_users.insert(17, 'IsDeleted', False)
df_users.insert(4, 'UserOwnerInfoId', pd.Series([None] * len(df_users), dtype="Int64"))
df_users.insert(5, 'UserTenantInfoId', pd.Series([None] * len(df_users), dtype="Int64"))

owner_counter = 1
tenant_counter = 1

# Asignar identificadores en propietarios y inquilinos
for index, row in df_users.iterrows():
    if row['RoleName'] == 'Owner':
        df_users.at[index, 'UserOwnerInfoId'] = owner_counter
        owner_counter += 1
    elif row['RoleName'] == 'Tenant':
        df_users.at[index, 'UserTenantInfoId'] = tenant_counter
        tenant_counter += 1

#===============================================================================================
## 2.4 Tabla de datos de UsersOwnersInfo
#===============================================================================================
# Filtar owner
filtered_UserOwner = df_users[df_users['RoleName'] == 'Owner']

# Seleccionar columnas y resetear index
df_UserOwnerInfo = filtered_UserOwner[['IsCompany', 'Id', 'CreatedAt', 'UpdatedAt', 'IsDeleted']].reset_index(drop=True)
UsersOwnersInfo = df_UserOwnerInfo.rename(columns={'Id': 'UserId'})

# Insertar Id
UsersOwnersInfo.insert(0, 'Id', range(1, len(df_UserOwnerInfo) + 1))

# Convertir IsCompany a tipo bool
UsersOwnersInfo['IsCompany'] = UsersOwnersInfo['IsCompany'].astype(bool)

#===============================================================================================
## 2.5 Tabla de datos de UsersTenantsInfo
#===============================================================================================
# Filtar Tenant
filtered_UserTenants = df_users[df_users['RoleName'] == 'Tenant']

df_UserTenantInfo = filtered_UserTenants[['Id', 'CreatedAt', 'UpdatedAt', 'IsDeleted']]
df_UserTenantInfo = df_UserTenantInfo.rename(columns={'Id': 'UserId'})

df_UserTenantInfo.insert(0, 'Id', range(1, len(df_UserTenantInfo) + 1))

# Merge usertenant con propiedades
df_UserTenantInfo = pd.merge(df_UserTenantInfo, df_prop[['Id', 'IsWorking', 'HasWarranty', 'SalaryId']], on='Id', how='inner')

UsersTenantsInfo = df_UserTenantInfo[['Id', 'IsWorking', 'HasWarranty', 'SalaryId', 'UserId', 'CreatedAt', 'UpdatedAt', 'IsDeleted']]

#===============================================================================================
## 2.6 Tabla de datos de Roles
#===============================================================================================
# Estableciendo tabla Roles
data_roles = [
    {"Id": 1, "RoleName": "Tenant"},
    {"Id": 2, "RoleName": "Owner"}
]
Roles = pd.DataFrame(data_roles)

Roles.loc[:, 'CreatedAt'] = datetime.now(pytz.UTC)
Roles['UpdatedAt'] = pd.Series([None] * len(Roles), dtype="datetime64[ns]")
Roles['IsDeleted'] = False

#===============================================================================================
## 2.7 Tabla de datos de Countries
#===============================================================================================
# Estableciendo tabla Paises
data_country = [
    {"Id": 1, "CountryName": "Argentina"}
]
Countries = pd.DataFrame(data_country)

Countries.loc[:, 'CreatedAt'] = datetime.now(pytz.UTC)
Countries['UpdatedAt'] = pd.Series([None] * len(Countries), dtype="datetime64[ns]")
Countries['IsDeleted'] = False

#===============================================================================================
## 2.8 Tabla de datos de States
#===============================================================================================
# Añadiedno pais a la tabla States
States['CountryId'] = 1
States.loc[:, 'CreatedAt'] = datetime.now(pytz.UTC)
States['UpdatedAt'] = pd.Series([None] * len(States), dtype="datetime64[ns]")
States['IsDeleted'] = False

#===============================================================================================
## 2.9 Tabla de datos de Genres
#===============================================================================================
# Estableciendo tabla Generos
data_genres = {
    1: "Male",
    2: "Female",
    3: "Non-binary",
    4: "Gender fluid",
    5: "Agender",
    6: "Bigender",
    7: "Demiboy",
    8: "DemiGirl"
}

Genres = pd.DataFrame(data_genres.items(), columns=["Id", "GenreName"])

Genres.loc[:, 'CreatedAt'] = datetime.now(pytz.UTC)
Genres['UpdatedAt'] = pd.Series([None] * len(Genres), dtype="datetime64[ns]")
Genres['IsDeleted'] = False

#===============================================================================================
## 2.10 Tabla de datos de Users
#===============================================================================================

Users = df_users.copy()

# Mapeo de la columnas Roles, pais, estados, generos con la columna 'Id' de sus respectivas tablas
Users["RoleName"] = Users["RoleName"].map(Roles.set_index("RoleName")["Id"])
Users["CountryName"] = Users["CountryName"].map(Countries.set_index("CountryName")["Id"])
Users["StateName"] = Users["StateName"].map(States.set_index("StateName")["Id"])
Users["GenreName"] = Users["GenreName"].map(Genres.set_index("GenreName")["Id"])

# Renombrar columnas
Users.rename(columns={'RoleName':'RoleId', 'CountryName':'CountryId', 
                                 'StateName':'StateId', 'GenreName':'GenreId' }, inplace=True)

Users.drop(["IsCompany"], axis=1, inplace=True)

#Transformando y cambiando el tipo de columnas
Users['BirthDate'] = pd.to_datetime(Users['BirthDate'], format='%d/%m/%Y', errors='coerce')
Users['IsProfileComplete'] = Users['IsProfileComplete'].astype(bool)
Users['Dni'] = Users['Dni'].astype(str)

#===============================================================================================
## 2.11 Tabla de datos de Images
#===============================================================================================
# Seleccionar columnas 
df_images = df_prop[['Id', 'img', 'CreatedAt', 'UpdatedAt', 'IsDeleted']]

df_images = df_images.rename(columns={'Id': 'PropertyId', 'img': 'ImageUrl'})

df_images.insert(0, 'Id', range(1, len(df_images) + 1))
df_images.insert(2, 'UserId', pd.Series([None] * len(df_images), dtype="Int64"))

Images = df_images.copy()

Images['ImageUrl'] = Images['ImageUrl'].apply(lambda x: eval(x) if isinstance(x, str) and x.startswith('[') else x)

#===============================================================================================
## 2.12 Tabla de datos de Requirements
#===============================================================================================
Requirements = UsersTenantsInfo.copy()
Requirements = Requirements[['Id', 'IsWorking', 'HasWarranty', 'SalaryId', 'CreatedAt', 'UpdatedAt', 'IsDeleted']]
Requirements['SalaryId'] = np.random.triangular(left=400000, mode=900000, right=3000000, size=len(Requirements))
Requirements = Requirements.rename(columns={'SalaryId':'RangeSalary'})

#===============================================================================================
## 2.13 Tabla de datos de Properties
#===============================================================================================
Properties = df_prop.copy()
Properties.drop(['IsWorking', 'HasWarranty', 'SalaryId'], axis=1, inplace=True)
Properties = Properties.merge(UsersTenantsInfo[['Id', 'UserId', ]], on='Id', how='inner')
Properties.insert(2, 'UserId', Properties.pop('UserId'))
Properties.rename(columns={'UserId': 'TenantId'}, inplace=True)

Properties = Properties.merge(UsersOwnersInfo[['Id', 'UserId']], on='Id', how='inner')
Properties.insert(2, 'UserId', Properties.pop('UserId'))
Properties.rename(columns={'UserId': 'OwnerId'}, inplace=True)

Properties.insert(4, 'RequirementId', range(1, len(Requirements) + 1))

Properties["CountryName"] = Properties["CountryName"].map(Countries.set_index("CountryName")["Id"])
Properties["StateName"] = Properties["StateName"].apply(lambda x: unidecode(x).lower()).map(
    States.set_index(States["StateName"].apply(lambda x: unidecode(x).lower()))["Id"]
)

Properties["img"] = Properties["img"].map(df_images.set_index("ImageUrl")["Id"])

Properties.drop('Id', axis=1, inplace=True)

Properties.rename(columns={'img': 'Id', 'CountryName': 'CountryId', 'StateName': 'StateId'}, inplace=True)

#arreglando la descripcion es muy largo solo acepta 100 varchar
Properties['Description'] = Properties['Description'].str.slice(0, 1000)
Properties['Title'] = Properties['Title'].str.slice(0, 50)
Properties['Address'] = Properties['Address'].str.slice(0, 50)

#===============================================================================================
## 3 Cargado de datos a una base de datos
#===============================================================================================

#Conexión a aws postgres database

usuario = 'Reffindr'
contraseña = 'uRnbS'
host = 'database-igrowker.cd0a0mu0w68g.us-east-2.rds.amazonaws.com'
dbname = 'intake004'
schema = 'ReffindrDBSchema'

DATABASE_URL = f"postgresql+psycopg2://{usuario}:{contraseña}@{host}:5432/{dbname}"
engine_aws = create_engine(DATABASE_URL, connect_args={"options": f"-csearch_path={schema}"})

print("Conexión exitosa")

# Eliminación de la columnas Ids

Requirements1 = Requirements.drop('Id', axis=1)
Properties1 = Properties.drop('Id', axis=1)
Images1 = Images.drop('Id', axis=1)
Users1 = Users.drop('Id', axis=1)
UsersOwnersInfo1 = UsersOwnersInfo.drop('Id', axis=1)
UsersTenantsInfo1 = UsersTenantsInfo.drop('Id', axis=1)


# Envio de datos a aws postgresql
Requirements1.to_sql("Requirements", engine_aws, schema=schema, if_exists="append", index=False)
print('Se subio tabla Requirements')

Properties1.to_sql("Properties", engine_aws, schema=schema, if_exists="append", index=False)
print('Se subio tabla Properties')

Images1.to_sql("Images", engine_aws, schema=schema, if_exists="append", index=False)
print('Se subio tabla Images')

Users1.to_sql("Users", engine_aws, schema=schema, if_exists="append", index=False)
print('Se subio tabla Users')

UsersOwnersInfo1.to_sql("UsersOwnersInfo", engine_aws, schema=schema, if_exists="append", index=False)
print('Se subio tabla UsersOwnersInfo')

UsersTenantsInfo1.to_sql("UsersTenantsInfo", engine_aws, schema=schema, if_exists="append", index=False)
print('Se subio tabla UsersTenantsInfo')












from geopy.geocoders import Nominatim
import re

# Función convertir precios a ARS
def convert_to_ars(price):
    exchange_rate = 1011.61 
    price = str(price)
    if 'USD' in price:
        price_numeric = float(price.replace('USD', '').replace('.', '').replace(',', '.').strip())
        return price_numeric * exchange_rate
    elif '$' in price:
        price_numeric = float(price.replace('$', '').replace('.', '').replace(',', '.').strip())
        return price_numeric
    else:
        return None
    
# Configuración de geolocalizador
geolocator = Nominatim(user_agent="geoapi_exercises")

# Función para obtener la dirección apartir de coordenadas
def obtener_direccion(lat, lon):
    if lat == 0.0 and lon == 0.0:
        return None 
    try:
        location = geolocator.reverse((lat, lon))
        return location.address if location else None
    except Exception as e:
        return f"Error: {e}"
    

# Función para extraer las últimas 4 partes de la dirección
def extract_relevant_address(address):
    parts = address.split(", ")
    return ", ".join(parts[-4:])

# Función para extraer el estado
def extract_state(relevant_address, states_list):
    for state in states_list:
        if re.search(rf'\b{re.escape(state)}\b', relevant_address):
            return state
    return None

# Función para asignar el rango
ranges = [
    (300000, 600000),
    (600000, 1000000),
    (1000000, 3000000),
    (3000000, float("inf"))
]
def assign_salary_range(salary):
    for i, (low, high) in enumerate(ranges, start=1):
        if low <= salary < high:
            return i
    return None

# Función para quitar los dos últimos elementos
def remove_last_two_parts(address):
    parts = address.split(', ')  
    return ', '.join(parts[:-2]) 



import requests
from bs4 import BeautifulSoup


def get_soup(url):
    """Devuelve un objeto BeautifulSoup de la URL especificada."""
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Error al obtener la página: {response.status_code}")
    return BeautifulSoup(response.text, 'html.parser')


def get_property_details(url_propiedad):
    """Obtiene los detalles de una propiedad individual."""
    response = requests.get(url_propiedad)
    soup = BeautifulSoup(response.text, 'html.parser')

    try:

        urls_img = [
            div['style'].split('url(')[1].split(')')[0]  
            for div in soup.find('div', {'class': 'hero-image-bg hero__3'}).find_all('div', style=True)
            if 'http' in div['style'] 
        ]

        country = soup.find('input', {'data-pais': True})['data-pais']
        
        item_owner_id = soup.find('p', {'class': 'property-code'})
        item_owner_id = item_owner_id.text.strip().split(":")[1].strip() if item_owner_id else None

        item_address = soup.find('p', {'class': 'location-container'})
        item_address_op = soup.find('h2', {'class': 'titlebar__title'})
        item_address = item_address.text.strip() if item_address else item_address_op.text.strip()

        item_price = soup.find('div', {'class': 'titlebar__price-mobile'}).find('p')
        item_price = item_price.text.strip() if item_price else None

        item_name = soup.find('p', {'class': 'form-details-heading'})
        item_name = item_name.text.strip() if item_name else None

        item_features = soup.find('ul', {'class': 'property-features'})
        if item_features:
            features = {}
            for li in item_features.find_all('li'):
                feature_name = li.find('p').contents[0].strip()
                feature_value = li.find('strong').text.strip()
                features[feature_name] = feature_value
        else:
            features = {}

        item_description = ', '.join([f"{key}{value}" for key, value in features.items()])

        n_ambiente = soup.find('li', title="Ambientes").find('div', class_='mobile').find('p', class_='strong')
        n_ambiente = n_ambiente.text.strip().split()[0] if n_ambiente else None

        n_banios = soup.find('li', title="Baños").find('div', class_='mobile').find('p', class_='strong')
        n_banios = n_banios.text.strip().split()[0] if n_banios else None

        n_dormitorios = soup.find('li', title="Dormitorios").find('div', class_='mobile').find('p', class_='strong')
        n_dormitorios = n_dormitorios.text.strip().split()[0] if n_dormitorios else None

        n_antiguedad = soup.find('li', title="Antigüedad").find('div', class_='mobile').find('p', class_='strong')
        n_antiguedad = n_antiguedad.text.strip().split()[0] if n_antiguedad and n_antiguedad.text.strip().split()[0].isdigit() else "0"

        return {
            'img': urls_img,
            'country': country,
            'owner_id': item_owner_id,
            'environments':n_ambiente,
            'bathrooms': n_banios,
            'bedrooms': n_dormitorios,
            'seniority': n_antiguedad,
            'address': item_address,
            'price': item_price,
            'description': item_description,
            'name': item_name
        }

    except Exception as e:
        print(f"Error procesando {url_propiedad}: {e}")
        return None


def get_properties_on_page(soup):
    """Extrae las propiedades de una página."""
    propiedades = soup.find_all('div', {'class': 'listing__item'})
    properties = []

    for propiedad in propiedades:
        try:
            url_pg_propiedad = propiedad.find('a', {'class': 'card'})['href']
            url_propiedad = f'https://www.argenprop.com{url_pg_propiedad}'
            details = get_property_details(url_propiedad)  # Llamada directa
            if details:
                properties.append(details)
        except Exception as e:
            print(f"Error procesando una propiedad: {e}")
    
    return properties


def get_next_page_url(soup):
    """Obtiene la URL de la siguiente página de la paginación."""
    next_page_item = soup.find('li', {'class': 'pagination__page-next pagination__page'})
    if next_page_item:
        next_page_link = next_page_item.find('a')['href']
        return f'https://www.argenprop.com{next_page_link}'
    return None


def scrape_properties(base_url, limite=None):
    """Realiza el scraping de todas las páginas hasta el límite especificado."""
    soup = get_soup(base_url)
    next_page = True
    casas = []
    page_count = 1

    while next_page:
        print(f"Scraping página {page_count}...")
        properties = get_properties_on_page(soup)
        casas.extend(properties)

        # Detener si alcanzamos el límite
        if limite and len(casas) >= limite:
            return casas[:limite]

        # Obtener la siguiente página
        next_page_url = get_next_page_url(soup)
        if next_page_url:
            soup = get_soup(next_page_url)
            page_count += 1
        else:
            next_page = False

    return casas

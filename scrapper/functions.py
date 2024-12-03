
import requests
from bs4 import BeautifulSoup
import time

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
        urls_img = []
        hero_image_div = soup.find('div', {'class': 'hero-image-bg hero__3'})
        if hero_image_div:
            urls_img = [
                div['style'].split('url(')[1].split(')')[0]
                for div in hero_image_div.find_all('div', style=True)
                if 'http' in div['style']
            ]
        
        country = soup.find('input', {'data-pais': True})
        country = country['data-pais'] if country else ""

        state = soup.find('input', {'data-provincia': True})
        state = state['data-provincia'] if state else ""

        title = soup.find('div', {'class': 'titlebar'})
        title = title.find('h2', {'class': 'titlebar__address'}).text.strip() if title and title.find('h2', {'class': 'titlebar__address'}) else ""

        latitud = soup.find('div', {'data-latitude': True})
        latitud = latitud['data-latitude'] if latitud else 0.0

        longitud = soup.find('div', {'data-longitude': True})
        longitud = longitud['data-longitude'] if longitud else 0.0

        price = soup.find('div', {'class': 'titlebar__price-mobile'})
        if price:
            price = price.find('p')
            price = price.text.strip() if price else 0

        n_ambiente = soup.find('li', title="Ambientes")
        if n_ambiente:
            n_ambiente = n_ambiente.find('div', class_='mobile').find('p', class_='strong')
            n_ambiente = n_ambiente.text.strip().split()[0] if n_ambiente else 0

        n_banios = soup.find('li', title="Baños")
        if n_banios:
            n_banios = n_banios.find('div', class_='mobile').find('p', class_='strong')
            n_banios = n_banios.text.strip().split()[0] if n_banios else 0

        n_dormitorios = soup.find('li', title="Dormitorios")
        if n_dormitorios:
            n_dormitorios = n_dormitorios.find('div', class_='mobile').find('p', class_='strong')
            n_dormitorios = n_dormitorios.text.strip().split()[0] if n_dormitorios else 0

        n_antiguedad = soup.find('li', title="Antigüedad")
        if n_antiguedad:
            n_antiguedad = n_antiguedad.find('div', class_='mobile').find('p', class_='strong')
            n_antiguedad = n_antiguedad.text.strip().split()[0] if n_antiguedad else 0
        else:
            n_antiguedad = 0

        n_antiguedad = n_antiguedad if str(n_antiguedad).isdigit() else 0

        description = soup.find('div', {'class': 'section-description--content'})
        description = description.text.strip() if description else ""

        return {
            'img': urls_img,
            'CountryName': country,
            'StateName': state,
            'Title': title,
            'Latitude': latitud,
            'Longitude': longitud,
            'Price': price,
            'Environments': n_ambiente,
            'Bathrooms': n_banios,
            'Bedrooms': n_dormitorios,
            'Seniority': n_antiguedad,
            'Description': description
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
            if not url_pg_propiedad:
                print(f"URL no encontrada para una propiedad.")
                continue

            url_propiedad = f'https://www.argenprop.com{url_pg_propiedad}'
            details = get_property_details(url_propiedad)
            if details:
                properties.append(details)
            else:
                print(f"Detalles no encontrados para {url_propiedad}")

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

def scrape_properties(base_url, limite=None, batch_size=100, sleep_time=2):
    """Realiza el scraping de todas las páginas hasta el límite especificado."""
    soup = get_soup(base_url)
    next_page = True
    casas = []
    page_count = 1

    while next_page:
        print(f"Scraping página {page_count}...")

        properties = get_properties_on_page(soup)
        casas.extend(properties)

        # Controlar el límite y tamaño de lote
        if limite and len(casas) >= limite:
            return casas[:limite]

        # Control de carga: Pausa después de cada lote
        if len(casas) % batch_size == 0:
            print(f"Esperando {sleep_time} segundos...")
            time.sleep(sleep_time)

        next_page_url = get_next_page_url(soup)
        if next_page_url:
            soup = get_soup(next_page_url)
            page_count += 1
        else:
            next_page = False

    return casas

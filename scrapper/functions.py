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
        # Obtener imágenes
        urls_img = [
            div['style'].split('url(')[1].split(')')[0]  
            for div in soup.find('div', {'class': 'hero-image-bg hero__3'}).find_all('div', style=True)
            if 'http' in div['style'] 
        ] if soup.find('div', {'class': 'hero-image-bg hero__3'}) else []

        # Obtener país
        country = soup.find('input', {'data-pais': True})['data-pais'] if soup.find('input', {'data-pais': True}) else None

        # Obtener state
        state = soup.find('input', {'data-provincia': True})['data-provincia'] if soup.find('input', {'data-provincia': True}) else None

        #Obtener Title
        title = soup.find('div', {'class': 'titlebar'})
        title = title.find('h2', {'class': 'titlebar__address'}).text.strip() if title else None

        # Obtener dirección
        latitud = soup.find('div', {'data-latitude': True})['data-latitude'] if soup.find('div', {'data-latitude': True}) else None
        longitud = soup.find('div', {'data-longitude': True})['data-longitude'] if soup.find('div', {'data-longitude': True}) else None

        # Obtener precio(Price)
        price = soup.find('div', {'class': 'titlebar__price-mobile'}).find('p') if soup.find('div', {'class': 'titlebar__price-mobile'}) else None
        price = price.text.strip() if price else None

        # Obtener número de ambientes(Environments)
        n_ambiente = soup.find('li', title="Ambientes")
        n_ambiente = n_ambiente.find('div', class_='mobile').find('p', class_='strong').text.strip().split()[0] if n_ambiente else None

        # Obtener número de baños(Bathrooms)
        n_banios = soup.find('li', title="Baños")
        n_banios = n_banios.find('div', class_='mobile').find('p', class_='strong').text.strip().split()[0] if n_banios else None

        # Obtener número de dormitorios(Bedrooms)
        n_dormitorios = soup.find('li', title="Dormitorios")
        n_dormitorios = n_dormitorios.find('div', class_='mobile').find('p', class_='strong').text.strip().split()[0] if n_dormitorios else None

        # Obtener antigüedad(Seniority)
        n_antiguedad = soup.find('li', title="Antigüedad")
        n_antiguedad = n_antiguedad.find('div', class_='mobile').find('p', class_='strong').text.strip().split()[0] if n_antiguedad else "0"
        n_antiguedad = n_antiguedad if n_antiguedad.isdigit() else "0"

        #Obtener descripción(Description)
        description = soup.find('div', {'class': 'section-description--content'}).text.strip() if soup.find('div', {'class': 'section-description--content'}) else None

        return {
            'img': urls_img,
            'CountryName': country,
            'StateName':state,
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

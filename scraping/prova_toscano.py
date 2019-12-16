from requests import get
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
from time import sleep


def process_price (price_string):
    """Strips a string of type '\n € 230.000 \n' and turns it into an integer 230000"""

    return int(
        ''.join(
            [char for char in price_string if char.isdigit()]
        ))


data = {
    'link' : [], 
    'price' : [], 
    'square_meters' : [],
    'price_per_sqm' : [],
    'rooms' : [], 
    'baths' : []
}

toscano_url = 'https://www.toscano.it'

for page_counter in range(6):
    # getting raw html
    webpage = get('https://www.toscano.it/vendita/immobili-residenziali/comune-roma/acilia-dragona-vitinia/' + repr(page_counter + 1))
    soup = BeautifulSoup(webpage.text, 'html.parser')

    houses = soup.find_all('div', class_ = 'row item')

    for house in houses:
        data['link'].append(
            toscano_url + house.find('div', 'col-xs-8 description').a['href']
        )
        house_info = house.find('div', class_ = 'row').find_all('div')

        data['price'].append(process_price(house_info[0].h4.string))
        data['square_meters'].append(int(house_info[1].h4.span.string))
        data['rooms'].append(house_info[2].h4.span.string)
        data['baths'].append(house_info[3].h4.span.string)

        data['price_per_sqm'].append(data['price'][-1] / data['square_meters'][-1])

    # this line prevets overloading the server with requests
    sleep(1)


del data['link']
form_data = pd.DataFrame(data)
print(form_data)
print(form_data['price_per_sqm'].mean())

from requests import get
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import pickle
from time import sleep
from geopy.geocoders import Nominatim
import csv


# string to integer parser
def to_number (string):
    """Strips a string of type '\n € 230.000 \n' and turns it into an integer 230000"""
    
    return int(
        ''.join(
            [char for char in string if char.isdigit()]
        ))


addr_header_options = [
	'via', 
	'Via', 
	'viale', 
	'Viale', 
	'piazza', 
	'Piazza', 
	'piazzale', 
	'Piazzale', 
	'largo', 
	'Largo'
]

def get_address (soup):
	try:
		title = soup.find('h1', class_='raleway title-detail').string
		
		for option in addr_header_options:
			addr_start = title.find(option)
			if addr_start >= 0:
				return title[addr_start:]
	except:
		error_log.write(f'{index},address\n')
		return ''


geolocator = Nominatim(user_agent='immobiliare-web_scraper')
def get_coordinates (address):
	try:
		location = geolocator.geocode(address)
		return location.latitude, location.longitude
	except:
		error_log.write(f'{index},coordinates\n')
		return 0.0,0.0


def get_floor (text):
	ind = text.find('>')
	floor = text[ind+1 : ind+2]

	if floor == 'S': return -1
	elif floor == 'T': return 0
	elif floor == 'A' or floor == 'R': return 100
	else: return int(floor)


condition_dict = {
	'Da ristrutturare' : 0,
	'Ottimo/Ristrutturato' : 2,
	'Ottimo / Ristrutturato' : 2,
	'Buono / Abitabile' : 1,
	'Buono/Abitabile' : 1
}
get_condition = lambda text: condition_dict[text]


# defining fields of interests for each house
columns=(
    'address', 
    'price',
    'square_meters',
    'rooms', 
    'baths',
    'floor',
    'type',
    'year_built',
    'condition',
    'energy_rating',
    'latitude',
    'longitude',
    'agency'
)


with open('house_list', 'rb') as house_file:
	house_links = pickle.load(house_file)


data_file = open('immobiliare_data_raw.csv', 'a')
error_log = open('immobiliare_errors.dat', 'a')

data_writer = csv.writer(
	data_file, 
	delimiter=',', 
	quotechar='"', 
	quoting=csv.QUOTE_MINIMAL
)
data_writer.writerow(columns)

starting_index = 10000
for index, house_link in enumerate(house_links[starting_index:]):
	index += starting_index
	
	try:
		webpage = get(house_link)
		soup = BeautifulSoup(webpage.text, 'html.parser')

		address = get_address(soup)
		latitude, longitude = get_coordinates(address)


		features = soup.find('div', class_='im-property__features')
		try:
			price = features.find('li', 'features__price').span.string
			price = to_number(price)
		except:
			error_log.write(f'{index},price\n')
			price = 0

		other_features = features.find('ul', 'list-inline list-piped features__list').find_all('li')
		try:
			rooms = to_number(other_features[0].div.span.string)
		except:
			error_log.write(f'{index},rooms\n')
			rooms = 0
		try:
			square_meters = to_number(other_features[1].div.span.string)
		except:
			error_log.write(f'{index},square_meters\n')
			square_meters = 0
		try:
			baths = to_number(other_features[2].div.span.string)
		except:
			error_log.write(f'{index},baths\n')
			baths = 0
		try:
			floor = get_floor(str(other_features[3].div.abbr))
		except:
			floor = -2

		data_tables = soup.find_all('div', class_='row section-data')

		try:
			house_type = data_tables[0].find_all('dd')[2].span.string
			# if there was no floor information maybe this is not an apartement
			if floor == -2:
				if house.find('vill') > -1 or house.find('Vill') > -1:
					floor = 0
				elif house.find('attico') > -1 or house.find('Attico') > -1:
					floor = 100
				else:
					error_log.write(f'{index},floor\n')
		except:
			error_log.write(f'{index},house_type\n')
			house_type = 'NA'
		try:
			year_built = data_tables[3].find_all('dd')[0].string
		except:
			error_log.write(f'{index},year_built\n')
			year_built = 0
		try:
			condition = data_tables[3].find_all('dd')[1].string
		except:
			error_log.write(f'{index},condition\n')
			condition = -1
		try:
			energy_rating = data_tables[3].find_all('dd')[4].string.strip()
		except:
			error_log.write(f'{index},energy_rating\n')
			energy_rating = 0
		try:
			agency = soup.find('p', class_='contact-data__name').a.string
		except:
			error_log.write(f'{index},agency\n')
			agency = 'NA'

		# appending row to dataframe
		data_writer.writerow([
			address, 
			price, 
			square_meters, 
			rooms, 
			baths, 
			floor, 
			house_type, 
			year_built, 
			condition, 
			energy_rating, 
			latitude, 
			longitude,
			agency
		])
	except:
		error_log.write(f'{index},link\n')

	if not index % 25: 
		data_file.flush()
		error_log.flush()

	# this line prevets overloading the server with requests
	sleep(0.5)
	print(f'Finished processing house {index}.')

data_file.close()
error_log.close()
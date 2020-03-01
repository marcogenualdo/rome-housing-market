from requests import get
from bs4 import BeautifulSoup
from time import sleep
import pickle


sleep_time = 0.5

# getting the number of pages
webpage = get('https://www.immobiliare.it/vendita-case/roma/?criterio=rilevanza&pag=1')
soup = BeautifulSoup(webpage.text, 'html.parser')

links_to_pages = soup.find('ul', class_='pagination pagination__number')
dead_links = soup.find_all('li', class_='disabled')
n_pages = int(dead_links[3].a.span.string)

time_to_complete = int(n_pages / 60 * sleep_time)
print(f'Getting links from {n_pages} pages. It will take about {time_to_complete} minutes.')


# getting links to individual house postings
house_links = []

for page_counter in range(n_pages):
    # getting raw html
    webpage = get('https://www.immobiliare.it/vendita-case/roma/?criterio=rilevanza&pag=' + repr(page_counter + 1))
    soup = BeautifulSoup(webpage.text, 'html.parser')

    houses = soup.find_all('p', class_='titolo text-primary')

    for house in houses:
    	house_links.append(house.a['href'])

    print(f'Page {page_counter} done, collected {len(house_links)} links so far.')
    sleep(sleep_time)


# saving list as Python bynary
out_file_name = 'house_list'
with open('../data/' + out_file_name, 'wb') as list_file:
	pickle.dump(house_links, list_file)

print(f'{len(house_links)} links saved to bynary {out_file_name}.')
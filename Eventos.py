import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd
from selenium import webdriver
import time


#É melhor fazer isso ou usar direto a URL com os termos de pesquisa usando operadores. Ex.: https://www.eventbrite.com.br/d/brazil/design-or-product-design-or-ux-or-javascript-or-react/
keywords = [
    'design', 'Product Design', 'ux', 'vendas', 'CAC', 'javascript', 'game', 'react', 'python', 'marketing', 'marketing digital', 'game design', 'design de jogos', 'mobile development', 'data science', 'web development',
    'product design', 'artificial intelligence', 'machine learning', 'product management', 'gestão de produto', 'UX writing', 'ux research', 'Front End', 'TypeScript', 'Swift', 'Objective-C', 'SQL', 'IA', 'inteligência artificial', 'AI', 'CocoaHeads', 'Java', 'Devs', 'Design Patterns', 'cloud', 'ruby', 'big data', 'startups', 'Web Development', 'php', 'banco de dados', 'mongodb', 'design gráfico', 'CX', 'Copywriting', 'Liderança', 'Cultura Organizacional', 'Business', 'Comunicação', 'Mídias', 'Estratégia', 'Gestão', 'Growth', 'Devops'

]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0',
}


csv_filename = 'events.csv'
csv_file = open(csv_filename, 'w', newline='', encoding='utf-8')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['Event Name', 'Event Description', 'Event Excerpt', 'Event Location', 'Event Venue Name', 'Event Organizer Name', 'Event Start Date', 'Event Start Time', 'Event End Date', 'Event End Time', 'Event Category', 'Event Tags', 'Event Cost', 'Event Featured Image', 'Event Website', 'Type of Event (Virtual, Hybrid)', 'Video Source URL'])

#Metup usa infinite scroll
#Como fazer quando o site força a geolocalização e/ou restringe a busca ampla (Ex.: Brasil) e força a busca por cidade?
#Aqui no Meetup usei o filtro 'any distance' para tentar pegar evento do Brasil inteiro
def scrape_meetup_events():
    base_url = 'https://www.meetup.com'
    
    for keyword in keywords:
        search_url = f'{base_url}/find/?keywords={keyword}&source=EVENTS&location=br--s&distance=anyDistance'
        response = requests.get(search_url, headers=headers)
        driver = webdriver.Chrome()
        driver.get(search_url)
        
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            
    if response.status_code == 200:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        events = soup.find_all('div', id='event-card-in-search-results')
            if not events:
                break

        for event in events:
            title = event.find('h1', class_='overflow-ellipsis overflow-hidden text-3xl font-bold leading-snug').text.strip()
            event_featured_image = event.find('picture', data-testid='event-description-image')
            description = event.find('div', id='event-details').text.strip()
            date = event.find('time', class_='').text.strip()
            location = event.find('div', data-testid='venue-name-value').text.strip()
            price = event.find('div', class_='font-semibold').text.strip()            
                   
            csv_writer.writerow([title, description, date, location])
                    
        else:
            print(f"Failed to fetch data for {keyword} (Page {page}). Status code: {response.status_code}")
            break
                
        driver.quit()

#Como fazer quando precisa clicar em "load more" para carregar mais resultados? E ela não muda com o carregamento.
def scrape_adplist_events():
    base_url = 'https://www.adplist.org/explore?tab=mentors&country=BR'
    
    for keyword in keywords:
        search_url = f'{base_url}'
        response = requests.get(search_url, headers=headers)
            
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        mentor_links = soup.find_all('div', class_='sc-dBmzty dGxpIk cursor-pointer')
            if not mentor_links:
                break

                for mentor_link in mentor_links:
                    mentor_url = mentor_link['href']
                    mentor_response = requests.get(mentor_url, headers=headers)
                    
                    if mentor_response.status_code == 200:
                        mentor_soup = BeautifulSoup(mentor_response.text, 'html.parser')
                        
                        title = mentor_soup.find('span', class_='mr-1').text.strip() #Como faz para expandir o show more?
                        description = mentor_soup.find('div', class_='About__Wrapper-sc-1xkh3p1-0 iWtCEz').text.strip() 
                        event_featured_image = event.find('div', class_='ProfilePhoto__Picture-sc-1fl76in-1 CKDXj')
                        date = event.find('p', class_='sc-jXbUNg kFsvSZ date__date').text.strip()
                        location = event.find('Evento online')   
                        community_stats = mentor_soup.find('div', class_='CommunityStats__CommunityStatsStyled-sc-ijjd2p-0 cdAhwe') #Como faz para expandir o show more?
                        price = event.find('Gratuito')
                        if community_stats:
                            description += '\nCommunity Stats: ' + community_stats.text.strip()
                        
                        mentor_background = mentor_soup.find('div', class_='ExperienceSection__Wrapper-sc-dr685y-2 iXdsSl')
                        if mentor_background:
                            description += '\nBackground: ' + mentor_background.text.strip()
                        
                        
                        csv_writer.writerow([title, description, '', ''])
                    else:
                        print(f"Failed to fetch data for mentor (Page {page}). Status code: {mentor_response.status_code}")
                        break
                    

def scrape_sympla_events():
    base_url = 'https://www.sympla.com.br'
    
    for keyword in keywords:
        page = 1
        while True:
            search_url = f'{base_url}/eventos?s={keyword}&page={page}'
            response = requests.get(search_url, headers=headers)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                events = soup.find_all('div', class_='CustomGridstyle__CustomGridCardType-sc-1ce1n9e-2 jMNblV')
                if not events:
                    break

                for event in events:
                    title = event.find('h1', class_='sc-983ba91-0 fypPvW').text.strip()
                    description = event.find('div', class_='sc-575bb398-0 emgExH').text.strip()
                    event_featured_image = event.find('div', class_='sc-1881a430-3 gXXriG')
                    date = event.find('div', class_='sc-983ba91-1 cZLMzD').text.strip()
                    location = event.find('div', class_='sc-983ba91-1 cZLMzD').text.strip()
                    price = event.find('div', class_='sc-28aed0db-3 cdOJAL').text.strip()
                    about_producer = event.find('div', class_='sc-93393ac5-1 bftFcy').text.strip()
                    if about_producer:
                            description += '\nAbout Producer: ' + about_producer.text.strip()
                    
                    
                    csv_writer.writerow([title, description, date, location])
                    
                page += 1
            else:
                print(f"Failed to fetch data for {keyword} (Page {page}). Status code: {response.status_code}")
                break

#Como fazer quando o site força a geolocalização e/ou restringe a busca ampla (Ex.: Brasil) e força a busca por cidade?
def scrape_eventbrite_events():
    base_url = 'https://www.eventbrite.com.br'
    
    for keyword in keywords:
        page = 1
        while True:
            search_url = f'{base_url}/d/brazil--s%C3%A3o-paulo/{keyword}/?page={page}&lang=pt
            response = requests.get(search_url, headers=headers)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                events = soup.find_all('section', class_='discover-horizontal-event-card')
                if not events:
                    break

                for event in events:
                    title = event.find('h1', class_='event-title css-0').text.strip()
                    description = event.find('div', class_='has-user-generated-content).text.strip()
                    event_featured_image = event.find('picture', data-testid='hero-image')
                    date = event.find('span', class_='date-info__full-datetime').text.strip()
                    location = event.find('p', class_='location-info__address-text').text.strip()
                    price = event.find('div', class_='conversion-bar__panel-info').text.strip()
                    
                    csv_writer.writerow([title, description, date, location])
                    
                page += 1
            else:
                print(f"Failed to fetch data for {keyword} (Page {page}). Status code: {response.status_code}")
                break
                

def scrape_events():
    scrape_meetup_events()
    scrape_adplist_events()
    scrape_sympla_events()
    scrape_eventbrite_events()
    
    csv_file.close()

if __name__ == "__main__":
    scrape_events()


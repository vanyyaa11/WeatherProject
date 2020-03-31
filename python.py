import sys
import html
import hashlib
import argparse
import configparser
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.request import urlopen, Request

ACCU_URL = "https://www.accuweather.com/uk/ua/lviv/324561/weather-forecast/324561"
ACCU_TAGS = ('<span class="large-temp">', '<span class="cond">')

DEFAULT_NAME = 'Kyiv'
DEFAULT_URL = 'https://www.accuweather.com/uk/ua/kyiv/324505/weather-forecast/324505'

ACCU_BROWSE_LOCATIONS = 'https://www.accuweather.com/uk/browse-locations'
CONFIG_LOCATION = 'Location'
CONFIG_FILE = 'weatherapp.ini'

CACHE_DIR = '.wappcache'

def get_request_headers():
    return {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0)'}


def get_cache_directory():
    """
        Path to cache directory
    """
    return Path.home() / CACHE_DIR


def get_url_hash(url):
    return hashlib.md5(url.encode('utf-8')).hexdigest()


def save_cache(url, page_source):
    """
        Save page source data to file
    """
    url_hash = get_url_hash(url)
    cache_dir = get_cache_directory()
    if not cache_dir.exists():
        cache_dir.mkdir(parents=True)
    with (cache_dir / url_hash).open('wb') as cache_file:
        cache_file.write(page_source)


def get_cache(url):
    """
        Return cache data if any.
    """
    cache = b''
    url_hash = get_url_hash(url)
    cache_dir = get_cache_directory()
    if cache_dir.exists():
        cache_path = cache_dir / url_hash
        if cache_path.exists():
            with cache_path.open('rb') as cache_file:
                cache = cache_file.read()

    return cache

def get_page_source(url):
    """
    """
    cache = get_cache(url)
    if cache:
        page_source = cache
    else:
        request = Request(url, headers=get_request_headers())
        page_source = urlopen(request).read()
        save_cache(url, page_source)

    return page_source.decode('utf-8')

def get_locations(locations_url):
    locations_page = get_page_source(locations_url)
    soup = BeautifulSoup(locations_page, 'html.parser')
   
    locations = []
    for location in soup.find_all(class_='search-result'):
        url = location.find('a').a['href']
        location = location.find('em').text
        locations.append((location, url))
    
    return locations



def get_configuration_file():
    return Path.home() / CONFIG_FILE

def save_configuration(name, url):
    parser = configparser.ConfigParser()
    parser[CONFIG_LOCATION] = {'name': name, 'url': url}
    with open(get_configuration_file(), 'w') as configfile:
        parser.write(configfile)

def get_configuration():
    name = DEFAULT_NAME
    url = DEFAULT_URL
    
    parser = configparser.ConfigParser()
    parser.read(get_configuration_file())
    if CONFIG_LOCATION in parser.sections():
        config = parser[CONFIG_LOCATION]
        name, url = config['name'], config['url']
    return name, url

def configurate():
    locations = get_locations(ACCU_BROWSE_LOCATIONS) 
    while locations:
        for index, location in enumerate(locations):
            print(f'{index + 1}. {location[0]}')
        selected_index = int(input('Please select location:'))
        location = locations[selected_index - 1]
        locations = get_locations(location[1])
        save_configuration(*location)


def get_weather_info(page_content):
    """
    """
    weather_info = {}
    weather_details = BeautifulSoup(page_content, 'html.parser')
    condition = weather_details.find('div', class_='cond')
    if condition:
        weather_info['cond'] = condition.text
    temp = weather_details.find('span', class_='high')
    if temp:
        weather_info['temp'] = temp.text
    feal_temp = weather_details.find('div', class_='real-feel')
    if feal_temp:
        weather_info['feal_temp'] = feal_temp.text
    wind_info = weather_details.find_all('li', class_='wind')
    if wind_info:
        weather_info['wind'] = \
            ' '.join(map(lambda t: t.text.strip(), wind_info))

    return weather_info


def produce_output(city_name, info):
    """
    """
    print('Accu Weather: \n')
    print(f'{city_name}')
    print('-'*20)

    for key, value in info.items():
        print(f'{key}: {html.unescape(value)}')

def get_accu_weather_info():
    city_name, city_url = get_configuration()
    content = get_page_source(city_url)
    produce_output(city_name, get_weather_info(content))

def main(argv):
    """
    Main entry point
    """


    KNOWN_COMMANDS = {'accu': get_accu_weather_info,
                      'config': configurate}

    parser = argparse.ArgumentParser()
    parser.add_argument('command',help='Service name', nargs=1)
    params = parser.parse_args(argv)

    # weather_sites = {"AccuWeather": (ACCU_URL, ACCU_TAGS)}

    if params.command:
        command = params.command[0]
        if command in KNOWN_COMMANDS:
                 KNOWN_COMMANDS[command]()
        else:
            print("Unknown command provided!")
            sys.exit(1)

if __name__ == '__main__':
    main(sys.argv[1:])

   
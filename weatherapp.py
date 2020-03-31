"""
 Weather app project
"""
import html
from urllib.request import urlopen, Request
ACCU_URL ="https://www.accuweather.com/uk/ua/lviv/324561/weather-forecast/324561"
headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0)'}
accu_request = Request(ACCU_URL, headers=headers)
accu_page = urlopen(accu_request).read()
accu_page = accu_page.decode('utf-8')
ACCU_TEMP_TAG = '<span class="high">'
accu_temp_tag_size = len(ACCU_TEMP_TAG)
accu_temp_tag_index = accu_page.find(ACCU_TEMP_TAG)
accu_temp_value_start = accu_temp_tag_index + accu_temp_tag_size
accu_temp = ' '
for char in accu_page[accu_temp_value_start:]:
    if char != '<':
        accu_temp += char
    else:
            break
ACCU_COND_TAG = '<div class="cond">'
accu_cond_tag_size = len(ACCU_COND_TAG)
accu_cond_tag_index = accu_page.find(ACCU_COND_TAG)
accu_cond_value_start = accu_cond_tag_index + accu_cond_tag_size
accu_cond = ' '
for char in accu_page[accu_cond_value_start:]:
    if char != '<':
        accu_cond += char
    else:
            break


print('AccuWeather: \n')
print(f'Temperature: {html.unescape(accu_temp)}\n')
print(f'Condition:{html.unescape(accu_cond)}\n')



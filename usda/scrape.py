import requests
from bs4 import BeautifulSoup

cookies = "JSESSIONID=7f00000130d9feab9be5b84f4612a677b69647e50d86.e38Obx8Sb3yQby0Lah0Ob40; _ga=GA1.2.1429948894.1450375486; __utma=77627408.1429948894.1450375486.1450375725.1450375725.1; __utmc=77627408; __utmz=77627408.1450375725.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utma=191960314.1429948894.1450375486.1450375725.1450375725.1; __utmc=191960314; __utmz=191960314.1450375725.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); oracle.uix=0^^GMT-5:00".split(';')

cookies = {k.split('=')[0].strip(): k.split('=')[1].strip() for k in cookies}

headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36'}

num = 1

data = "_id33=2&resultview%3A_id293%3A_id394%3A_id567=&resultview%3A_id293%3A_id394%3A1%3A_id424%3ArangeStart=0&resultview%3A_id293%3A_id394%3ArangeStart=0&oracle.adf.faces.FORM=CustomerForm&oracle.adf.faces.STATE_TOKEN=7a&event=&source=resultview%3A_id293%3A_id394%3A" + str(num) + "%3Ainspdetailshow"

data = data.split('&')

data = {k.split('=')[0].strip(): k.split('=')[1].strip() for k in data}

html = requests.post('https://acissearch.aphis.usda.gov/LPASearch/faces/CustomerSearch.jspx', data=data, headers=headers, cookies=cookies)

print html.text

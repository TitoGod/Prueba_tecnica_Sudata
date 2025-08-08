# Comprobar robots.txt y permiso de crawling

import urllib.robotparser
from urllib.parse import urljoin

base = "https://www.argenprop.com"
rp = urllib.robotparser.RobotFileParser()
rp.set_url(urljoin(base, "/robots.txt"))
rp.read()

user_agent = "mi-scraper/1.0"
url_a_testear = "https://www.argenprop.com/terrenos/venta/posadas"

# Si el resultado es True, se puede hacer scraping
print("robots.txt consultado:", rp.url)
print("Se puede fetchear con este user-agent?", rp.can_fetch(user_agent, url_a_testear))
if rp.can_fetch(user_agent, url_a_testear):
    print(f"Se puede hacer scraping de {url_a_testear} con el user-agent '{user_agent}'")
else:
    print(f"No se puede hacer scraping de {url_a_testear} con el user-agent '{user_agent}'")
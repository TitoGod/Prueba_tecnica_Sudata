# Comprobar bloqueos técnicos con requests

import requests

headers = {"User-Agent": "Mozilla/5.0 (compatible; MiBot/1.0; +https://miweb.example)"}
r = requests.get("https://www.argenprop.com/terrenos/venta/posadas", headers=headers, timeout=10, allow_redirects=True)

# Imprimir información de la respuesta
print("status_code: ", r.status_code)
print("Encabezados: ",r.headers.get("Server"))
print("Tiene Cloudflare?: ",r.headers.get("CF-Ray"))   # Si existe, indica Cloudflare
print(len(r.text))
# mirar parte del HTML para notar "Attention required" (Cloudflare) o formularios de captcha
print(r.text[:800])
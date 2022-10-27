import requests

def get_wfs(url, service, request, version, typenames, bbox, srsname):
    
    query = f"{url}?SERVICE={service}&REQUEST={request}&version={version}&TYPENAMES={typenames}&bbox={bbox}&SRSNAME={srsname}"

    response = requests.get(query)

    if response.status_code == 200:
        with open('radko.gml', 'wb') as f:
            f.write(response.content)
    else:
        print(f" adres {response} zwrócił kod {response.status_code}")

url = 'https://geoportal.powiat.kielce.pl/map/geoportal/wfs.php' 
service = 'WFS'
request = 'GetFeature'
version = '2.0.0'
typenames = 'ewns:dzialki'
bbox = '324922,607897,326156,611727'
srsname = 'EPSG:2180'

get_wfs(url, service, request, version, typenames, bbox, srsname)

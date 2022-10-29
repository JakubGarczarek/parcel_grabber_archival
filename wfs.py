import requests

# pobranie działek w gml z podanego bboxa w usłudze wfs :

def wfs(url, service, request, version, typenames, bbox, srsname):
    
    query = f"{url}?SERVICE={service}&REQUEST={request}&version={version}&TYPENAMES={typenames}&bbox={bbox}&SRSNAME={srsname}"

    response = requests.get(query)

    if response.status_code == 200:
        with open('radko.gml', 'wb') as f:
            f.write(response.content)
    else:
        print(f" adres {response} zwrócił kod {response.status_code}")


# pobranie działek z uldk, na podst. teytów w pliku csv:

def uldk(csv, metoda, format, output):
    with open(csv) as f:
        for line in f:
            teryt=line.strip()
            querry= f"https://uldk.gugik.gov.pl/?request=GetParcelById&id={teryt}&result={format}"
            response = requests.get(querry)
            pobrana_geom = str(response.content)[5:-3]
            with open(f"{output}", "a",encoding = 'utf-8') as f:
                f.write(pobrana_geom+"\n")
            print(pobrana_geom)


# parametry niezbędne dla funkcji wfs i jej wywołanie:

url = 'https://geoportal.powiat.kielce.pl/map/geoportal/wfs.php' 
service = 'WFS'
request = 'GetFeature'
version = '2.0.0'
typenames = 'ewns:dzialki'
bbox = '324922,607897,326156,611727'
srsname = 'EPSG:2180'

wfs(url, service, request, version, typenames, bbox, srsname)


# parametry niezbędne do funkcji uldk i jej wywołanie:

csv = 'dzialki.csv'
metoda = 'GetParcelById'
#metoda = 'GetAggregateArea'
format = 'geom_wkt'
# format = 'geom_extend'
output = 'output.txt'

uldk(csv, metoda, format, output)
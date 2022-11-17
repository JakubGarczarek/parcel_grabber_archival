# pobranie działek w gml z podanego bboxa w usłudze wfs
 
import requests, re
from bs4 import BeautifulSoup

def get_wfs(url, service, request, version, typenames, bbox, srsname):
    
    query = f"{url}?SERVICE={service}&REQUEST={request}&version={version}&TYPENAMES={typenames}&bbox={bbox}&SRSNAME={srsname}"

    response = requests.get(query)

    if response.status_code == 200:
        with open('radko.gml', 'wb') as f:
            f.write(response.content)
    else:
        print(f" adres {response} zwrócił kod {response.status_code}")

def gml_to_wkt(gml_file):
    with open(gml_file, 'r') as f:
        file = f.read() 
        soup = BeautifulSoup(file,'xml')
        geometrie = soup.find_all('gml:posList')
        xy=[]
        for geom in geometrie:
            coord=re.findall("\d+\.\d+",geom.text)
            xs = coord[0::2]
            ys = coord[1::2]
            coord2 = []
            geom2 = ''
            for x in xs:
                point = f"{ys[xs.index(x)]} {x}"
                geom2 += point
            wkt = f"POLYGON(('{geom2}'))"
            print(wkt)
            with open(f"{gml_file}.wkt", "a",encoding = 'utf-8') as f:
                                f.write(wkt+"\n")
                       
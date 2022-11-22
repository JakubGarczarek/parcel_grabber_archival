# pobranie działek w gml z podanego bboxa w usłudze wfs
 
import requests, re
from bs4 import BeautifulSoup
from postgis import wkt_to_postgis
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
        gml_Polygons = soup.findAll('gml:Polygon')
        for gml_Polygon in gml_Polygons:
            ewns_geometria = gml_Polygon.parent
            ewns_ID_DZIALKI = ewns_geometria.find_previous_sibling('ewns:ID_DZIALKI')
            teryt = ewns_ID_DZIALKI.text
            gml_posLists = gml_Polygon.findAll('gml:posList')
            points = []
            print(teryt)
            for gml_posList in gml_posLists:
                extracted_xy = re.findall("\d+\.\d+", gml_posList.text)
                extracted_x = extracted_xy[0::2]
                extracted_y = extracted_xy[1::2]
                reversed_xy = ''
                for x in extracted_x:
                    point = f"{extracted_y[extracted_x.index(x)]} {x},"
                    reversed_xy += point
                points.append(f"({reversed_xy[:-1]})")
            wkt = 'POLYGON('
            for polygon in points:
                wkt += f"{polygon},"
            wkt = wkt[:-1] + ')'
            print(wkt)
            with open(f"{gml_file}.wkt", "a",encoding = 'utf-8') as f:
                                    f.write(teryt+"\n")
                                    f.write(wkt+"\n")
    
def gml_to_postgis(gml_file, connection, tab):
    with open(gml_file, 'r') as f:
        file = f.read() 
        soup = BeautifulSoup(file,'xml')
        gml_Polygons = soup.findAll('gml:Polygon')
        for gml_Polygon in gml_Polygons:
            ewns_geometria = gml_Polygon.parent
            ewns_ID_DZIALKI = ewns_geometria.find_previous_sibling('ewns:ID_DZIALKI')
            teryt = ewns_ID_DZIALKI.text
            gml_posLists = gml_Polygon.findAll('gml:posList')
            points = []
            print(teryt)
            for gml_posList in gml_posLists:
                extracted_xy = re.findall("\d+\.\d+", gml_posList.text)
                extracted_x = extracted_xy[0::2]
                extracted_y = extracted_xy[1::2]
                reversed_xy = ''
                for x in extracted_x:
                    point = f"{extracted_y[extracted_x.index(x)]} {x},"
                    reversed_xy += point
                points.append(f"({reversed_xy[:-1]})")
            wkt = 'POLYGON('
            for polygon in points:
                wkt += f"{polygon},"
            wkt = wkt[:-1] + ')'
            print(wkt)
            wkt_to_postgis(connection, tab, teryt, wkt)

# pobranie działek z uldk, na podst. teytów w pliku csv

import requests, re
import geopandas as gpd
from sqlalchemy import create_engine
from postgis import wkt_to_postgis

def min_max_xy(geom):
    xy_list = re.findall("\d+\.\d+",geom)
    x_list = xy_list[0::2]
    y_list = xy_list[1::2]
    min_x = min(x_list)
    min_y = min(y_list)
    max_x = max(x_list)
    max_y = max(y_list)
    return [min_x, min_y, max_x, max_y]
    
def compare_xy(minmax1, minmax2):
    smaller_x = min(minmax1[0], minmax2[0])
    smaller_y = min(minmax1[1], minmax2[1])
    bigger_x = max(minmax1[2], minmax2[2])
    bigger_y = max(minmax1[3], minmax2[3])
    return(smaller_x, smaller_y, bigger_x, bigger_y)

def bbox_from_csv(csv, metoda, format, output):
    compare_list=[]
    with open(csv) as f:
        for line in f:
            teryt=line.strip()
            querry= f"https://uldk.gugik.gov.pl/?request={metoda}&id={teryt}&result={format}"
            response = requests.get(querry)
            if response.status_code == 200:
                xy = re.search('POLYGON\(\((.+?)\)\)', str(response.content)).group(1)
                geometria = f"POLYGON(({xy}))"
                to_compare = min_max_xy(geometria)
                compare_list.append(to_compare)
                if len(compare_list)==2:
                    latest = compare_xy(compare_list[0], compare_list[1])
                    compare_list=[latest]
                    print(compare_list)
                # with open(f"{output}", "a",encoding = 'utf-8') as f:
                #     f.write(geometria+"\n")
                # print(geometria)
            else:
                print(f" adres {response} zwrócił kod {response.status_code}")
                with open(f"braki_{output}", "a",encoding = 'utf-8') as f:
                    f.write(teryt+"\n")
                print(f"zapisuję {teryt} do braki_{output}")
    return f"{compare_list[0][1]},{compare_list[0][0]},{compare_list[0][3]},{compare_list[0][2]}"
def uldk_to_csv(csv, metoda, format, output):
    with open(csv) as f:
        for line in f:
            teryt=line.strip()
            querry= f"https://uldk.gugik.gov.pl/?request={metoda}&id={teryt}&result={format}"
            response = requests.get(querry)
            if response.status_code == 200:
                xy = re.search('POLYGON\(\((.+?)\)\)', str(response.content)).group(1)
                geometria = f"POLYGON(({xy}))"
                with open(f"{output}", "a",encoding = 'utf-8') as f:
                    f.write(geometria+"\n")
                print(geometria)
            else:
                print(f" adres {response} zwrócił kod {response.status_code}")
                with open(f"braki_{output}", "a",encoding = 'utf-8') as f:
                    f.write(teryt+"\n")
                print(f"zapisuję {teryt} do braki_{output}")


def uldk_to_postgis(csv, metoda, format, connection, tab):
    with open(csv) as f:
        for line in f:
            teryt=line.strip()
            querry= f"https://uldk.gugik.gov.pl/?request={metoda}&id={teryt}&result={format}"
            response = requests.get(querry)
            if response.status_code == 200:
                xy = re.search('POLYGON\(\((.+?)\)\)', str(response.content)).group(1)
                geometria = f"POLYGON(({xy}))"
                wkt_to_postgis(connection, tab, teryt, geometria)
                # with open(f"{output}", "a",encoding = 'utf-8') as f:
                #     f.write(geometria+"\n")
                print(geometria)
            else:
                print(f" adres {response} zwrócił kod {response.status_code}")
                with open(f"braki_{connection}", "a",encoding = 'utf-8') as f:
                    f.write(teryt+"\n")
                print(f"zapisuję {teryt} do braki_{connection}")
# pobranie działek z uldk, na podst. teytów w pliku csv

import requests, re
import geopandas as gpd
from sqlalchemy import create_engine
from postgis import wkt_to_postgis

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
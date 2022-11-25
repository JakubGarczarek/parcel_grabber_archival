import requests, re
from postgis import wkt_to_postgis

class Bbox():

    """Wyznaczanie bboxa dla podanej listy terytów działek"""

    def __init__(self, csv, output): #wymaga podania źródła terytów (csv) i do jakiego pliku zapisać niepowodzenia(output)
        self.csv = csv #źródło teyrtów (np. baza gruntów w csv)
        self.output = output #do jakiego pliku zapisać niepowodzenia
        self.metoda = 'GetParcelById' #parametr do zapytania ULDK, może być też 'GetAggregateArea'
        self.format = 'geom_wkt' #parametr do zapytania ULDK,domyślnie jest geom_wkb, może być też geom_extend

    def bbox_from_csv(self): #przyjmuje csv z listą terytów, zwraca xy narożników bboxa w stringu pasującego do zapytania WFS (pion, poziom)
        compare_list = [] #utworzenie pustej listy porównawczej, do której później wpadać będą pary kompletów (listy) współrzędnych
        with open(self.csv) as f:
            for line in f: #iteracja przez wszystkie linie pliku csv z terytami
                teryt = line.strip() #pobranie terytu z oczyszczonej linii pliku csv
                querry= f"https://uldk.gugik.gov.pl/?request={self.metoda}&id={teryt}&result={self.format}" #taki jest format zapytania http ULDK
                response = requests.get(querry) #użycie biblioteki request do wykonania ww. zapytania
                if response.status_code == 200: #zabezpieczenie przed błędami połączenia
                    xy = re.search('POLYGON\(\((.+?)\)\)', str(response.content)).group(1)#wydobycie samych współrzędnych z contentu zapytania
                    geometria = f"POLYGON(({xy}))" #opakowanie współrzędnych formatem wkt
                    to_compare = self.min_max_xy(geometria) #wrzucenie do funkcji zwracającej LISTĘ min i max współrzędnych przygotowany wyżej wkt
                    compare_list.append(to_compare) #dodanie ww. LISTY min i max współrzędnych do przygotowanej wcześniej listy porównawczej
                    if len(compare_list)==2: #działanie gdy aktualnie w liście porównawczej znajdują się 2 komplety (listy) wspórzędnych
                        latest = self.compare_xy(compare_list[0], compare_list[1]) #wysyłka 2 list z ekstremami, zwrotka stringa z minX, minY, maxX, maxY i do zmiennej
                        compare_list=[latest] #redukcja zawartości listy porównawczej z 2 podlist do 1 listy zawierającej ww. min i max wsp z tych 2 pierwotnych list
                        print(compare_list) #żeby nie pomyśleć że skrypt wisi ;)
                else: #działania gdyby serwer z uldk nie odpowiedział
                    print(f" adres {response} zwrócił kod {response.status_code}")
                    with open(f"braki_{self.output}", "a",encoding = 'utf-8') as f:
                        f.write(teryt+"\n") #zapisanie do pliku terytów bez odpowiedzi
                    print(f"zapisuję {teryt} do braki_{self.output}") #info o powyższym dla usera
        bbox = f"{compare_list[0][1]},{compare_list[0][0]},{compare_list[0][3]},{compare_list[0][2]}" #min Y, min X, max Y, max X w stringu do zmiennej,
        return bbox #którą finalnie zwrócimy

    def min_max_xy(self, geom): #potrzebna tylko do bbox_from_csv(), zwraca listę min max współrzędnych z dostarczonego wkt
        xy_list = re.findall("\d+\.\d+",geom) #wydobycie samych współrzędnych z dostarczonego wkt i do listy
        x_list = xy_list[0::2] #wydobycie samych x z powyższych współrzędnych i do listy
        y_list = xy_list[1::2] #wydobycie samych y z powyższczych współrzędnych i do listy
        min_x = min(x_list) # wydobycie najmniejszych x z powyższych współrzędnych i do zmiennej
        min_y = min(y_list) # wydobycie najmniejszych y z powyższych współrzędnych i do zmiennej
        max_x = max(x_list) # wydobycie największych x z powyższych współrzędnych i do zmiennej
        max_y = max(y_list) # wydobycie największych y z powyższych współrzędnych i do zmiennej
        return [min_x, min_y, max_x, max_y] #zwrot powyższych min i max w postaci listy
    
    def compare_xy(self, minmax1, minmax2): #potrzebna tylko do bbox_from_csv(), przyjmuje 2 listy min i max współrzędnych, zwraca ich min i max współrzędne luzem
        smaller_x = min(minmax1[0], minmax2[0]) # min z samych najmniejszych x'ów
        smaller_y = min(minmax1[1], minmax2[1]) # min z samych najmniejszych y'ków
        bigger_x = max(minmax1[2], minmax2[2])  # max z samych największych x'ów
        bigger_y = max(minmax1[3], minmax2[3]) # max z samych największych y'ków
        return(smaller_x, smaller_y, bigger_x, bigger_y) #zwrot

    def save_to_file(self, file): # zapisuje bboxa zwróconego przez bbox_from_csv do dowolnego pliku
        with open (file, "a", encoding='utf-8') as f: #otwarcie pliku w którym zapisany zostanie bbox
            f.write(self.bbox_from_csv()) #zapis bboxa do podanego pliku (uruchamia całą metodę bbox_from_csv)


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



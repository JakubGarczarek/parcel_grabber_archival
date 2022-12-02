import requests, re, json

class ULDK():

    def __init__(self, csv):
        self.csv = csv

    ###################################################
    # CSV (lista TERYTÓW) => JSON {"TERYT":"GEOM_WKT"}
    ###################################################

    def json(self):
        # narazie pusty słownik {"TERYT":"GEOM_WKT"}
        teryt_geom = {}
        # otwieramy csv z terytami
        with open(self.csv) as csv:
            for line in csv:
                # pobranie pojedynczego terytu z csv
                teryt = line.strip()
                # zapytanie do usługi uldk z podaniem terytu
                querry= f"https://uldk.gugik.gov.pl/?request=GetParcelById&id={teryt}&result=geom_wkt"
                response = requests.get(querry)
                # gdy serwer odpowie poprawnie i coś zwróci w content
                if response.status_code == 200:
                    # serwer zwraca wkt z białymi znakami
                    wkt_uncleaned = str(response.content)
                    # czyścimy 
                    # wyciągnięcie samych współrzędnych
                    only_xy = re.search('POLYGON\(\((.+?)\)\)', wkt_uncleaned).group(1) 
                    # ponowne opakowanie ich w POLYGON(()) wg formatu wkt
                    geom = f"POLYGON(({only_xy}))"
                    # dodanie do słownika pojedynczej pary {"TERYT":"GEOM_WKT"}
                    teryt_geom[teryt] = geom
                # gdy brak odpowiedzi z serwera lub content pusty
                else:
                    # utwórz plik o nazwie jak csv ale z prefixem "braki" (nadpisanie)
                   with open(f"braki_{self.csv}", "w",encoding = 'utf-8') as f:
                    # zapisz w nowej lini teryt którego geometrii serwer nie zwrócił
                        f.write(teryt+"\n")  
                    
        # zapis słownika {"TERYT":"GEOM_WKT"} do pliku JSON (nadpisanie)
        with open (f"{self.csv}.json", "w", encoding='utf-8') as f:
            json.dump(teryt_geom, f)
        # dodatkowo zwrotka finalnego wyniku (nie tylko json)
        return teryt_geom
    


    ####################################
    # JSON {"TERYT":"GEOM_WKT"} => BBOX
    ####################################

    def bbox(self):
        #utworzenie pustej listy porównawczej, 
        # do której później wpadać będą pary kompletów (listy) współrzędnych
        compare_list = []
        #otworzenie jsona stworzonego przez uldk.json()
        with open(f"{self.csv}.json") as f:
            j = json.load(f)
            # iteracja przez wszystkie pary {"TERYT":"GEOM_WKT"} z jsona
            for geom in j.values():
                # wyodrębnienie samych liczb (współrzędnych) z geom (do listy)
                xy_list = re.findall("\d+\.\d+",geom)
                # lista samych x-ów (co 2 element od 0)
                x_list = xy_list[0::2]
                # lista samych y-ków (co 2 element od 1)
                y_list = xy_list[1::2]
                # dodanie ich extremów do utworzonej wcześniej listy porównawczej
                compare_list.append( [min(x_list), min(y_list), max(x_list), max(y_list)] )
                # Jeżeli w tej liście znajduje się aktualnie
                # komplet (para) list współrzędnych do porównania
                # tworzymy z nich jedną listę z ekstremami 
                if len(compare_list) == 2:
                    # pobranie kompletów ekstremów do zmiennych a i b
                    # a oraz b to listy o strukturze [min x, min y, max x, max y]
                    a = compare_list[0]
                    b = compare_list[1]
                    # najmniejszy x min (pomiędzy a i b)
                    ab_min_x = min(a[0], b[0])
                    # najmniejszy y min (pomiędzy a i b)
                    ab_min_y = min(a[1], b[1])
                    # największy x max (pomiędzy a i b)
                    ab_max_x = max(a[2], b[2])
                    # największy y max (pomiędzy a i b)
                    ab_max_y = max(a[3], b[3])
                    # zastąpienie a i b w compare_list 
                    # na jedną listę zawierającą ekstrema 
                    # z porównania a i b
                    compare_list = [[ab_min_x, ab_min_y, ab_max_x, ab_max_y]]
                    
                # jeśli compare_list zawiera tylko 1 element pomijamy redukcję a i b 
                # (bo jest tylko nowe a) i wracamy do początku pętli w celu dodania 
                # kolejnego b    
        # finalnie compare_list zawiera jedną zwycięzką listę [0]
        # z której wyciągniemy wsp bboxa
        x_min = compare_list[0][0]
        y_min = compare_list[0][1]
        x_max = compare_list[0][2]
        y_max = compare_list[0][3]
        # usługa wfs potrzebuje stringa z odwróconymi wspołrzędnymi
        # oddzielonymi przecinkami
        bbox = f"{y_min},{x_min},{y_max},{x_max}"
        # zapis bboxa do pliku
        with open (f"bbox_{self.csv}", 'w', encoding='utf-8') as f:
            f.write(bbox)
        return bbox

  
    ####################################
    # CSV + ORGANY.JSON => URL
    ####################################

    def url(self):
        # lista do wrzucania wystąpień danego terytu
        licz_teryty = []
        with open(self.csv) as csv:
            for line in csv:
                # pobrabnie 4 pierwszych cyfr terytu
                teryt_powiatu = line.strip()[:4]
                licz_teryty.append(teryt_powiatu)
        # najczęściej występujący teryt
        best_teryt = max(licz_teryty, key=licz_teryty.count)
        # pobranie danych z jsona przygotowanego
        # jednorazowo przez json_exporter.py
        with open ('organy.json') as f:
            d = json.load(f)
        for param in d.values():
            # porównanie z 4 pierwszymi cyframi terytu działki
            if best_teryt == param['teryt'][:4]:
            # wyciągnięcie urla i obcięcie apostrofów
                wfs_url = param['url'][1:-1]
        #zapis url do pliku
        with open(f"url_{self.csv}", 'w', encoding='utf-8') as f:
            f.write(wfs_url)
        return wfs_url

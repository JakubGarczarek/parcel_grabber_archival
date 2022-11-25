import requests, re, json

class Uldk():

    def __init__(self, csv):
        self.csv = csv
    
    # stworzenie słownika {"TERYT":"GEOM_WKT"}

    def json_teryt_geom(self):
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
        # dodatkowo poza jsonem zwrot słownika {"TERYT":"GEOM_WKT"} przez funkcję
        return teryt_geom


# przykład użycia metody json_teryt_geom()
# wskazujemy na plik csv z listą terytów działek
csv = 'testowy.csv'
# tworzymy obiekt uldk dostarczając ścieżkę do csv z terytami
uldk = Uldk(csv)
# wywołanie metody i zapisanie terytów i geometrii do zmiennej(słownik)
dane = uldk.json_teryt_geom()


    




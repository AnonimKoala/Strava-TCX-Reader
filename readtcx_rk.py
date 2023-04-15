# Robert Kubasiak ~ 2023 ~ Wszelkie prawa zastrzeżone
import geopy.distance
from datetime import datetime
import xml.etree.ElementTree as ET
import re


def read_tcx(file_name):
    # Otwiera plik
    xml_file = open(file_name, 'r')

    # Odczytuje plik do zmiennej xml_str
    xml_str = xml_file.read()

    # Zastępuje niepotrzebny nagłówek na pusty string
    xml_str = re.sub(' xmlns="[^"]+"', '', xml_str, count=1)

    # Tworzy obiekt root z xml_str
    root = ET.fromstring(xml_str)

    # Znajduje wszystkie elementy Activity
    activities = root.findall('.//Activity')

    # Tworzy listę w której będą wszystkie dane aktywności
    data_activ_list = []

    for activity in activities:
        # Wyświetla nazwę aktywności

        # Znajduje wszystkie elementy Trackpoint
        tracking_points = activity.findall('.//Trackpoint')

        for tracking_point in list(tracking_points):
            # Tworzy listę z elementów Trackpoint - lista czas, puls, pozycja, itd.
            children = list(tracking_point)

            # Tworzy słownik tymczasowo w którym będą dane z listy elementów Trackpoint
            dict_temp = {}

            # Iteruje po elementach Trackpoint
            for childValue in children:

                # Zapisuje do słownika dane z elementów Trackpoint
                match childValue.tag:
                    case "Time":
                        # Zmienia format daty z ISO na YYYY-MM-DD HH:MM:SS
                        date = datetime.fromisoformat(
                            childValue.text[:-1] + '+00:00')

                        # Zapisuje czas i datę
                        dict_temp['Date'] = date.strftime(
                            '%Y-%m-%d')  # YYYY-MM-DD
                        dict_temp['Time'] = date.strftime(
                            '%H:%M:%S')  # HH:MM:SS

                    case "HeartRateBpm":    # Zapisuje do słownika puls jeśli występuje
                        dict_temp[childValue.tag] = int(childValue[0].text)

                    # Zapisuje kadencję (obroty korby na minutę)
                    case "Cadence":
                        dict_temp[childValue.tag] = int(childValue.text)

                    case "Position":        # Zapisuje pozycję
                        # Szerokość geograficzną
                        dict_temp["Latitude"] = childValue[0].text
                        # Długość geograficzną
                        dict_temp["Longitude"] = childValue[1].text

                    case "AltitudeMeters":  # Zapisuje wysokość n.p.m.
                        dict_temp['Altitude'] = float(childValue.text)

                    case "DistanceMeters":  # Zapisuje przebyty dystans w km
                        # Zaokrągla w celu uniknięcia rozbieżności
                        dict_temp['Distance'] = round(
                            float(childValue.text) / 1000, 4)
                        
                if dict_temp.get('Cadence') == None:
                    dict_temp['Cadence'] = 0
                if dict_temp.get('HeartRateBpm') == None:
                    dict_temp['HeartRateBpm'] = 0
                
                

            # Dodaje do danych aktywności dane z Trackpoint'u
            data_activ_list.append(dict_temp)

            # Oblicza prędkość, jeśli jest więcej niż 1 element w liście i różnica czasu między 2 elementami jest różna od 0
            if len(data_activ_list) > 1 and ((datetime.strptime(data_activ_list[-1]['Time'], '%H:%M:%S') - datetime.strptime(data_activ_list[-2]['Time'], '%H:%M:%S')).total_seconds() / 3600) != 0:
                # Oblicza prędkość 'dystansowoą' na podstawie dystansu
                data_activ_list[-1]['Velocity_Distance'] = round(
                    (float(data_activ_list[-1]['Distance']) -
                     float(data_activ_list[-2]['Distance']))
                    / round((datetime.strptime(data_activ_list[-1]['Time'], '%H:%M:%S') - datetime.strptime(data_activ_list[-2]['Time'], '%H:%M:%S')).total_seconds() / 3600, 4), 2)

                # Oblicza prędkość na podstawie współrzędnych geograficznych
                data_activ_list[-1]['Velocity_Geo'] = round(
                    geopy.distance.geodesic((float(data_activ_list[-1]['Latitude']), float(data_activ_list[-1]['Longitude'])), (float(
                        data_activ_list[-2]['Latitude']), float(data_activ_list[-2]['Longitude']))).km
                    / round((datetime.strptime(data_activ_list[-1]['Time'], '%H:%M:%S') - datetime.strptime(data_activ_list[-2]['Time'], '%H:%M:%S')).total_seconds() / 3600, 4), 2)
                
                data_activ_list[-1]['Avg_Velocity'] = data_activ_list[-1]['Distance'] / (datetime.strptime(data_activ_list[-1]['Time'], '%H:%M:%S') - datetime.strptime(data_activ_list[0]['Time'], '%H:%M:%S')).total_seconds() * 3600



                # Zmienia prędkość dystansową ostatniego pomiaru na prędkość dystansową z przed ostatniego pomiaru, jeśli prędkość w pomiarze ostatnim jest większa o 25 km/h niż w poprzednim pomiarze
                if len(data_activ_list) > 3 and data_activ_list[-1]['Velocity_Distance'] - 25 > data_activ_list[-2]['Velocity_Distance']:
                    data_activ_list[-1]['Velocity_Distance'] = data_activ_list[-2]['Velocity_Distance']

                # Zmienia prędkość geograficzną ostatniego pomiaru na prędkość geograficzną z przed ostatniego pomiaru, jeśli prędkość w pomiarze ostatnim jest większa o 25 km/h niż w poprzednim pomiarze
                if len(data_activ_list) > 3 and data_activ_list[-1]['Velocity_Geo'] - 25 > data_activ_list[-2]['Velocity_Geo']:
                    data_activ_list[-1]['Velocity_Geo'] = data_activ_list[-2]['Velocity_Geo']


                # Oblicza średnią prędkość z prędkości dystansowej i geograficznej
                data_activ_list[-1]['Velocity'] = (
                    (data_activ_list[-1]['Velocity_Distance'] + data_activ_list[-1]['Velocity_Geo']) / 2
                )
                # Jeśli prędkość w pomiarze ostatnim jest większa o 25 km/h niż w poprzednim pomiarze
                if len(data_activ_list) > 3 and data_activ_list[-1]['Velocity'] - 25 > data_activ_list[-2]['Velocity']:
                    # Zmienia prędkość ostatniego pomiaru na prędkość z przed ostatniego pomiaru
                    data_activ_list[-1]['Velocity'] = data_activ_list[-2]['Velocity']

            else:   # Jeśli nie, to ustawia prędkości na 0
                data_activ_list[-1]['Velocity'] = 0
                data_activ_list[-1]['Velocity_Distance'] = 0
                data_activ_list[-1]['Velocity_Geo'] = 0

    # Zamyka plik
    xml_file.close()

    data_activ_list[0]['Avg_Velocity'] = 0
    return data_activ_list

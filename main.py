# Robert Kubasiak ~ 2023 ~ Wszelkie prawa zastrzeżone
import pandas as pd
import matplotlib.pyplot as plt
import readtcx_rk as rt

# Pobiera nazwę pliku z konsoli
path = input('Podaj nazwę pliku z rozszerzeniem .tcx umieszczoną w folderze activities np. ride.tcx:\n')

# Sprawdza czy plik ma rozszerzenie .tcx
if not path.endswith('.tcx'):
    print('Niepoprawne rozszerzenie pliku')
    exit()

# Sprawdza czy plik istnieje
try:
    open(f"activities/{path}", 'r')
except FileNotFoundError:
    print('Nie ma takiego pliku')
    exit()

# Odczyt pliku tcx
activity = rt.read_tcx(f"activities/{path}")

# Tworzy obiekt DataFrame z listy danych aktywności
df = pd.DataFrame(activity)


# Wyświetla menu
print('Wybierz zadanie:\n1. Wykres prędkości od dystansu\n2. Wykres średniej prędkości od dystansu\n3. Wykres wysokości od dystansu\n4. Kadencji od dystansu\n5. Wykres pulsu od dystansu\n6. Wykres prędkości od średniej')
print('7. Średnia prędkość')
print('8. Średni puls')
print('9. Średnia wysokość')
print('10. Średnia kadencja')
print('11. Export do csv')
print('12. Wyjście')


while True:
    # Wybiera zadanie
    task = input('Wybór: ')

    # Wykonuje zadanie
    match task:
        case '1':
            df.plot(x='Distance', y='Velocity', kind='line')
            plt.show()
        case '2':
            df.plot(x='Distance', y='Avg_Velocity', kind='line', color='purple')
            plt.show()
        case '3':
            df.plot(x='Distance', y='Altitude', kind='line', color='grey')
            plt.show()
        case '4':
            df.plot(x='Distance', y='Cadence', kind='line', color='black')
            plt.show()
        case '5':
            df.plot(x='Distance', y='HeartRateBpm', kind='line', color='red')
            plt.show()
        case '6':
            plt.plot(df['Distance'], df['Velocity'], label='Velocity')
            plt.plot(df['Distance'], df['Avg_Velocity'], label='Avg_Velocity', color='purple')
            plt.legend()
            plt.show()
        case '7':
            print(f"Średnia prędkość: {df['Velocity'].mean():.2f} km/h")
        case '8':
            print(f"Średni puls: {df['HeartRateBpm'].mean():.2f} bpm")
        case '9':
            print(f"Średnia wysokość: {df['Altitude'].mean():.2f} m")
        case '10':
            print(f"Średnia kadencja: {df['Cadence'].mean():.2f} rpm")
        case '11':
            df.to_csv(f"csv/{path}_export.csv", sep=';', decimal=',', index=False)
        case '12':
            exit()
        case _:
            print('Nie ma takiego polecenia')

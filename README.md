# Wykrywanie upadku z użyciem ADXL345 i STM32F103

## 1. Wprowadzenie
Projekt ma na celu wykrywanie upadku z wykorzystaniem akcelerometru ADXL345 oraz mikrokontrolera STM32F103.
Dane z czujnika są przesyłane do komputera przez interfejs USB, gdzie mogą być analizowane i wizualizowane.
Opracowano dwa podejścia:
1. **Algorytm manualny** - oparty o progi i analize próbek z czujnika
2. **Model uczenia maszynowego** - oparty o klasyfikator trenujący się na zbiorach danych przy pracy czujnika

Najważniejsze ręczne zmiany w kodzie źródłowym znajdują się w plikach:
- `main.c` – główna logika programu, wykrywanie upadku, konfiguracja parametrów.
- `adxl345.c` – obsługa komunikacji z czujnikiem ADXL345.

Pozostałe pliki zostały wygenerowane i modyfikowane automatycznie przez środowisko STM32CubeIDE.

## 2. Komunikacja
W projekcie zastosowano dwie magistrale komunikacyjne:
- **I2C** – komunikacja pomiędzy akcelerometrem ADXL345 a mikrokontrolerem STM32.
- **USB** (CDC) – komunikacja pomiędzy STM32 a komputerem PC.
Dane pomiarowe są przesyłane cyklicznie do komputera i mogą być przetwarzane na różne sposoby.

## 3. Programy do odbioru danych
### 4.1. `rx_adxl.py`
Skrypt w Pythonie umożliwiający odczyt danych i wyświetlanie ich w konsoli.
(tu zdjęcie)
### 4.2. `rx_adxl_visualization.py`
Program do wizualizacji danych w czasie rzeczywistym na wykresach.
(tu zdjęcie)

## 4. Algorytm manualny
W implementacji manualnej wykorzystano proste warunki:
- jeśli wartość przyspieszenia spadła poniżej określonego progu (`FREEFALL_LIMIT_MS2`), licznik `freeFallCount` był inkrementowany,
- licznik ten był resetowany, gdy sygnał wracał do normy szybciej niż po x próbkach (TUTAJ SPRAWDZ NAZWE ZMIENNEJ I NAPISZ)
- aby uznać zdarzenie za upadek, musiało to trwać przez określoną liczbę próbek (np. 30–50),
- dodatkowy warunek na minimalną różnicę między kolejnymi próbkami (np. > 20), aby odróżnić upadek od machania ręką,
- dodatkowo po spadku musiał nastąpić szybki wzrost (peak) sygnału.
Parametry wykrywania upadku:
```c
#define FREEFALL_LIMIT_MS2   6.0f
#define FREEFALL_MIN_SAMPLES 200
#define IMPACT_THRESHOLD     50.0f
#define IMPACT_DELTA_MIN     20.0f
#define DEBOUNCE_TIME_MS     1000
```
- **FREEFALL_LIMIT_MS2** – graniczna wartość przyspieszenia (m/s²), poniżej której traktujemy ruch jako swobodny spadek.
- **FREEFALL_MIN_SAMPLES** – minimalna liczba próbek, przez które spadek musi trwać, aby został uznany.
- **IMPACT_THRESHOLD** – minimalna wartość przyspieszenia po spadku, interpretowana jako uderzenie.
- **IMPACT_DELTA_MIN** – różnica wartości między kolejnymi próbkami, aby odróżnić uderzenie od machania.
- **DEBOUNCE_TIME_MS** – minimalny czas pomiędzy kolejnymi detekcjami upadków.

## 5. Uczenie maszynowe
### 5.1. Okna czasowe
Dane z akcelerometru są bardzo szumne, dlatego pojedyncze próbki nie wystarczają do rozpoznania upadku.  
Zamiast tego stosowano **okna czasowe** (np. 150–160 próbek).
Dla każdego okna liczono dodatkowe cechy (features), aby ująć **dynamikę sygnału w czasie**, a nie tylko chwilowe wartości.

### 5.2. Ekstrahowane cechy
Dla każdej osi **X, Y, Z**, a także sygnałów pochodnych:
- **A** – całkowite przyspieszenie (`sqrt(X^2 + Y^2 + Z^2)`) TUTAJ SPRAWDZ CZY DA SIE ROWNANIE NAPISAC,
- **DX, DY, DZ, DA** – różnice kolejnych próbek,

wyliczano zestaw cech statystycznych:
- średnia (`mean`),
- odchylenie standardowe (`std`),
- minimum i maksimum,
- zakres (max – min),
- energia sygnału (`sum(x^2)`).

Te cechy tworzyły wektor wejściowy dla modelu ML.

### 5.3. Modele ML
Przetestowane modele:
- **Random Forest** (200 drzew, z balansowaniem klas),
- **XGBoost** (200 drzew, `scale_pos_weight` dla klas niezrównoważonych).

Oba modele działały dobrze, jednak **ostatecznie wybrano Random Forest**, ponieważ:
- dawał stabilniejsze wyniki,
- był prostszy do implementacji i eksportu (pickle → później możliwość konwersji do C). TUTAJ SPRAWDZ CYZ NAPEWNO

## 5. Analiza danych w Jupyter Notebook

### 5.1. Wykrywanie upadku przez algorytm manualny

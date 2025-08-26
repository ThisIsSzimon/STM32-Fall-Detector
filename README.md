# Wykrywanie upadku z użyciem ADXL345 i STM32F103

## 1. Wprowadzenie
Projekt ma na celu wykrywanie upadku z wykorzystaniem akcelerometru ADXL345 oraz mikrokontrolera STM32F103.
Dane z czujnika są przesyłane do komputera przez interfejs USB, gdzie mogą być analizowane i wizualizowane.

Najważniejsze ręczne zmiany w kodzie źródłowym znajdują się w plikach:
- `main.c` – główna logika programu, wykrywanie upadku, konfiguracja parametrów.
- `adxl345.c` – obsługa komunikacji z czujnikiem ADXL345.

Pozostałe pliki zostały wygenerowane i modyfikowane automatycznie przez środowisko STM32CubeIDE.

## 2. Parametry wykrywania upadku z poziomu mikrokontrolera
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

## 3. Komunikacja
W projekcie zastosowano dwie magistrale komunikacyjne:
- **I2C** – komunikacja pomiędzy akcelerometrem ADXL345 a mikrokontrolerem STM32.
- **USB** (CDC) – komunikacja pomiędzy STM32 a komputerem PC.
Dane pomiarowe są przesyłane cyklicznie do komputera i mogą być przetwarzane na różne sposoby.

## 4. Programy do odbioru danych
### 4.1. rx_adxl.py
Skrypt w Pythonie umożliwiający odczyt danych i wyświetlanie ich w konsoli.

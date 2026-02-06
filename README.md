# PROJEKT SEMESTRALNY - Analiza porównawcza baz danych przestrzennych: BDOT10k vs OpenStreetMap

## 📝 Opis projektu
Projekt semestralny zrealizowany w celu porównania dokładności geometrycznej oraz atrybutowej warstwy **budynków** w dwóch azach danych:
* **BDOT10k** (Baza Danych Obiektów Topograficznych) – oficjalny polski rejestr państwowy.
* **OpenStreetMap (OSM)** – globalny projekt mapowania społecznościowego.

Celem analizy było sprawdzenie stopnia pokrycia danych, różnic w liczbie obiektów oraz weryfikacja, jak dane społecznościowe (OSM) wypadają na tle oficjalnych danych geodezyjnych.

---

## 📂 Struktura plików
Kod zorganizowany jest w sposób modułowy:

### 2. Pliki pomocnicze
Zawierają definicje funkcji, które są importowane i wykorzystywane w pliku głównym:
* **`odzipowanie.py`** – Zawiera funkcję "nested_zip", która wypakowuje określone pliki z wielu ZIP-ów znajdujących się w danym folderze do folderu docelowego
* **`rozne.py`** – Zawiera większość funkcji używanych w pliku głównym, funkcje są stworzone możliwie najbardziej uniwersalnie z myślą o przyszłym ich użyciu
* 
### 1. Plik główny
* **`ps_s.py`** – Główny skrypt sterujący procesem, oparty na funkcjach pomocnicznych


---

## 💻 Wymagania (Technologie)
Projekt wykorzystuje głównie domyślne biblioteki języka Python oraz **arcpy** zależne od ArcGIS Pro

---

Oto gotowy rozdział do pliku README.md, który szczegółowo opisuje proces przetwarzania danych (tzw. Pipeline). Dodałem go w formie czytelnej listy krok po kroku, co świetnie pokazuje logikę Twojego kodu.

Markdown

---

## ⚙️ Etapy przetwarzania danych (Data Pipeline)

Proces analizy został podzielony na 10 kluczowych kroków, które zapewniają spójność danych i umożliwiają ich porównanie:

1. **Ekstrakcja danych**: Automatyczne wypakowanie warstw budynków według klucza:
   * `BUBD_A` dla bazy BDOT10k.
   * `buildings_a` dla bazy OpenStreetMap.
2. **Unifikacja nazw OSM**: Dodanie do nazw plików OSM prefiksu (pierwsze 5 liter nazwy folderu nadrzędnego), aby uniknąć konfliktów nazw i nadpisywania plików w geobazie.
3. **Normalizacja nazewnictwa**: Oczyszczenie nazw plików poprzez zamianę kropek na podkreślenia (`.` -> `_`), co gwarantuje stabilne działanie narzędzi GIS i baz danych.
4. **Import do geobazy**: Automatyczne przeniesienie wszystkich przygotowanych plików do struktury geobazy projektowej.
5. **Agregacja BDOT**: Łączenie rozproszonych arkuszy BDOT dla całego województwa w jedną warstwę z przyrostkiem `_Polaczone`.
6. **Optymalizacja struktury**: Usunięcie zbędnych, cząstkowych warstw BDOT po poprawnym zakończeniu procesu łączenia.
7. **Reprojekcja (Układ współrzędnych)**: Transformacja danych OSM z układu geograficznego `WGS84` na układ płaski `PL-1992` (EPSG:2180), zgodny z BDOT10k.
8. **Generowanie statystyk warstw**: Tworzenie raportu podsumowującego dla każdej warstwy, zawierającego:
   * Nazwę warstwy.
   * Liczbę poligonów (budynków).
   * Łączną powierzchnię zabudowy [km²].
9. **Analiza przestrzenna w siatce**: Generowanie siatki wektorowej o oczku **10x10 km** dla obszaru badań.
10. **Wyznaczanie różnic**: Uzupełnienie siatki o atrybuty różnicy w liczbie budynków oraz ich powierzchni między obiema bazami dla każdego pola siatki.



---

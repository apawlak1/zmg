import arcpy
import os
import shutil
import rozne    #to jest moj plik z funkcjami :D
import odzipowanie

print('START!!!!!!!!')

#wybieram geobaze i pliki z danymi (fl to 'file', chce uniknac pomylek)
workspace = r'C:\Users\olaa3\Documents\ArcGIS\Projects\projekt_sem\projekt_sem.gdb'
bdot_folder = r'C:\PROJEKT\Polska_SHP'
osm_folder = r'C:\PROJEKT\OSM_SHP'

#folder posredni z samymi budynkami zeby troche 'odchudzic' dane
export_folder = r'C:\PROJEKT\BUDYNKI'

'''
odzipowanie.nested_zip(bdot_folder, export_folder, 'BUBD_A')
odzipowanie.nested_zip(osm_folder, export_folder, 'buildings_a')


arcpy.env.overwriteOutput = True
arcpy.env.workspace = workspace


#najpierw zmmieniam kropki w nazwach z BDOT na podlogi
rozne.fname_change(export_folder, '.', '_')
print('juz ;P')


rozne.import2gdb(export_folder, workspace)
print('JUPIIII IMPOROTWANE')



# --- LOGIKA ŁĄCZENIA GRUPAMI ---
print("Rozpoczynam grupowanie i łączenie warstw BDOT...")
arcpy.env.workspace = workspace
lista_w_bazie = arcpy.ListFeatureClasses()

# 1. Tworzymy słownik, gdzie kluczem jest 34 znaki, a wartością lista pasujących warstw
grupy_warstw = {}

for n in lista_w_bazie:
    if "bubd_a" in n.lower() and "polaczone" not in n.lower():
        prefix = n[:34] # bierzemy pierwsze 34 znaki jako klucz grupy
        if prefix not in grupy_warstw:
            grupy_warstw[prefix] = []
        grupy_warstw[prefix].append(os.path.join(workspace, n))

# 2. Iterujemy po grupach i łączymy tylko te, które mają więcej niż 1 plik
for prefix, warstwy in grupy_warstw.items():
    warstwa_wynikowa = os.path.join(workspace, f"{prefix}_Polaczone")
    
    if not arcpy.Exists(warstwa_wynikowa):
        if len(warstwy) >= 2:
            print(f"Łączę grupę {prefix} ({len(warstwy)} warstw)...")
            arcpy.management.Merge(warstwy, warstwa_wynikowa)
            arcpy.management.DeleteIdentical(warstwa_wynikowa, ["Shape"])
        else:
            # Jeśli jest tylko jedna warstwa w grupie, po prostu ją kopiujemy jako "Polaczone"
            # albo zostawiamy jak jest - tutaj decydujemy o eksporcie
            print(f"Grupa {prefix} ma tylko jedną warstwę, kopiuję...")
            arcpy.management.CopyFeatures(warstwy[0], warstwa_wynikowa)
    else:
        print(f"Warstwa {prefix}_Polaczone już istnieje, pomijam.")

# 3. Definiujemy bdot_final do dalszych analiz 
# Jeśli po złączeniu chcesz analizować WSZYSTKIE budynki BDOT razem, 
# musisz zrobić jeszcze jeden merge wszystkich "Polaczone" do jednej warstwy bdot_final:

wszystkie_polaczone = [os.path.join(workspace, n) for n in arcpy.ListFeatureClasses("*_Polaczone")]



# --- CZYSZCZENIE WARSTW PZGIK ---
print("Usuwanie zbędnych warstw PZGIK (bez końcówki _Polaczone)...")
arcpy.env.workspace = workspace
lista_fc = arcpy.ListFeatureClasses()

licznik_usunietych = 0

for fc in lista_fc:
    # Warunek: nazwa zawiera 'PZGIK' ORAZ nie kończy się na '_Polaczone'
    if "PZGIK" in fc.upper() and not fc.endswith("_Polaczone"):
        try:
            arcpy.management.Delete(fc)
            licznik_usunietych += 1
            # print(f"Usunięto: {fc}")
        except Exception as e:
            print(f"Błąd podczas usuwania {fc}: {e}")

print(f"Zakończono czyszczenie PZGIK. Usunięto {licznik_usunietych} warstw resztkowych.")


#UWAGA ANALIZY
# Naprawiamy dane OSM
rozne.fix_spatial_and_area(workspace, 'buildings')
'''


# URUCHOMIENIE ANALIZ
#rozne.gdb_stats(workspace)
rozne.generuj_siatke_roznicy_polska_OSM(workspace, bok_metry=10000)


print('KONIEC ROBOTY!')
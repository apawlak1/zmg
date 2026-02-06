import os
import arcpy
import shutil

#---1. ta funkcja zmienia 'symbol_before' na 'symbol_after', przede wszystkim do miany kropek na podlogi---
def fname_change(folder_path, stary_znak='.', nowy_znak='_'):
    print(f'Zmieniam znaki '{stary_znak}' na '{nowy_znak}' w folderze: {folder_path}')
    licznik = 0

    for plik in os.listdir(folder_path):
        #oddzielenie nazwy od rozszerzenia
        nazwa_rdzen, rozszerzenie = os.path.splitext(plik)

        if stary_znak in nazwa_rdzen:
            nowa_nazwa_rdzen = nazwa_rdzen.replace(stary_znak, nowy_znak)
            nowy_plik = nowa_nazwa_rdzen + rozszerzenie
            
            stara_sciezka = os.path.join(folder_path, plik)
            nowa_sciezka = os.path.join(folder_path, nowy_plik)

            try:
                os.rename(stara_sciezka, nowa_sciezka)
                licznik += 1
            except Exception as e:
                print(f'Blad przy zmianie nazwy {plik}: {e}')

    print(f'Zmieniono nazwy {licznik} plikow.')

            
#---2. import do geobazy---
def import2gdb(shp_folder, gdb_workspace):
    arcpy.env.workspace = shp_folder
    feature_classes = arcpy.ListFeatureClasses() 
    
    if not feature_classes:
        print('Brak plikow .shp w folderze')
        return

    for fc in feature_classes:
        output_name = os.path.splitext(fc)[0] 
        target_path = os.path.join(gdb_workspace, output_name)
        
        if not arcpy.Exists(target_path):
            print(f'Importuje warstwe wektorowa: {output_name}...')
            #dedykowane narzedzie ArcGIS do konwersji
            arcpy.conversion.FeatureClassToFeatureClass(fc, gdb_workspace, output_name)
        else:
            print(f'{output_name} juz istnieje')


#---3. reprojekcja---
def fix_spatial_and_area(workspace, klucz, target_epsg=2180):
    #przez konwersje EPSG wymuszone jest przeliczenie powierzchni
    arcpy.env.workspace = workspace
    target_sr = arcpy.SpatialReference(target_epsg)
    lista_fc = arcpy.ListFeatureClasses()

    for fc in lista_fc:
        if klucz.lower() in fc.lower():
            sciezka_fc = os.path.join(workspace, fc)
            desc = arcpy.Describe(fc)
            
            # 1. Sprawdzamy czy uklad jest inny niz docelowy
            # Jesli jest inny, Project automatycznie przeliczy Shape_Area na metry kw.
            if desc.spatialReference.factoryCode != target_epsg:
                temp_fc = f'{fc}_reprojected'
                temp_path = os.path.join(workspace, temp_fc)
                
                # Kluczowy krok: Project aktualizuje systemowe pole Shape_Area
                arcpy.management.Project(sciezka_fc, temp_path, target_sr)
                
                # Zamieniamy stara warstwe na nowa (z poprawnym Shape_Area)
                arcpy.management.Delete(sciezka_fc)
                arcpy.management.Rename(temp_path, fc)
            
            else:
                # Jesli uklad byl juz OK, warto zrobic Repair Geometry, 
                # zeby odswiezyc tabele systemowa
                arcpy.management.RepairGeometry(fc)

    print(f'Zakonczono reprojekcje dla '{klucz}' \n')

#---4. liczenie ogolnej liczby obiektow na danej warstwie---
def gdb_stats(workspace):
    arcpy.env.workspace = workspace
    lista_fc = arcpy.ListFeatureClasses()
    
    print(f'{'WARSTWA':<40} | {'LICZBA':<10} | {'SUMA POW. [m2]':<15}')
    print('-' * 75)

    for fc in lista_fc:
        try:
            liczba = int(arcpy.management.GetCount(fc)[0])
            
            #sumowanie pow
            suma_pow = 0

            with arcpy.da.SearchCursor(fc, ['Shape_Area']) as cursor:
                for row in cursor:
                    if row[0]:
                        suma_pow += row[0]
            
            #tabelka w konsoli
            print(f'{fc:<40} | {liczba:<10} | {suma_pow:,.2f}')
            
        except Exception as e:
            print(f'Blad przy warstwie {fc}: {e}')

    print('-' * 75)

    

#---4. siatka (to ostatnie do stworzenia mapy)---
def generuj_siatke_roznicy_polska_OSM(workspace, bok_metry=10000):
    arcpy.env.workspace = workspace
    arcpy.env.overwriteOutput = True
    
    fcs = arcpy.ListFeatureClasses()
    
    #laczenie warstw budynkow
    warstwy_bdot = [fc for fc in fcs if 'BUBD_A' in fc.upper() and 'SIATKA' not in fc.upper()]
    warstwy_osm = [fc for fc in fcs if 'OSM' in fc.upper() and 'SIATKA' not in fc.upper()]

    bdot_all = arcpy.management.Merge(warstwy_bdot, os.path.join('memory', 'bdot_all'))
    osm_all = arcpy.management.Merge(warstwy_osm, os.path.join('memory', 'osm_all'))

    # 2. Pobranie zasiegu z ogolnopolskiego OSM (Wersja ucinajaca - corner_coord)
    desc_osm = arcpy.Describe(osm_all)
    ext = desc_osm.extent
    
    siatka_wynik = os.path.join(workspace, 'Siatka_Roznic_Polska_OSM_BASE')

    arcpy.management.CreateFishnet(
        out_feature_class=siatka_wynik,
        origin_coord=f'{ext.XMin} {ext.YMin}',
        y_axis_coord=f'{ext.XMin} {ext.YMin + 10}',
        cell_width=bok_metry,
        cell_height=bok_metry,
        number_rows=0,
        number_columns=0,
        corner_coord=f'{ext.XMax} {ext.YMax}',
        labels='NO_LABELS',
        template=ext,
        geometry_type='POLYGON'
    )
    arcpy.management.DefineProjection(siatka_wynik, arcpy.SpatialReference(2180))

    #spatial join (agregacja)
    def agreguj(grid, source, prefix):
        print(f'Agreguje {prefix}')
        fms = arcpy.FieldMappings()
        fm = arcpy.FieldMap()
        fm.addInputField(source, 'Shape_Area')
        f_name = fm.outputField
        f_name.name = f'sum_pow_{prefix}'
        fm.outputField = f_name
        fms.addFieldMap(fm)

        temp_j = os.path.join('memory', f'j_{prefix}')
        arcpy.analysis.SpatialJoin(grid, source, temp_j, 'JOIN_ONE_TO_ONE', 'KEEP_ALL', fms, 'INTERSECT')
        arcpy.management.JoinField(grid, 'OID', temp_j, 'TARGET_FID', ['Join_Count', f'sum_pow_{prefix}'])
        arcpy.management.AlterField(grid, 'Join_Count', f'count_{prefix}', f'Liczba_{prefix}')
        arcpy.management.Delete(temp_j)

    agreguj(siatka_wynik, bdot_all, 'bdot')
    agreguj(siatka_wynik, osm_all, 'osm')

    #obliczenie atrybutow do wizualizacja
    print('Obliczanie roznicy (OSM - BDOT)...')
    arcpy.management.AddFields(siatka_wynik, [
        ['roznica_sztuk', 'LONG', 'Roznica Liczby (OSM-BDOT)'],
        ['roznica_pow', 'DOUBLE', 'Roznica Powierzchni (OSM-BDOT)']
    ])

    fields = ['count_bdot', 'count_osm', 'sum_pow_bdot', 'sum_pow_osm', 'roznica_sztuk', 'roznica_pow']
    with arcpy.da.UpdateCursor(siatka_wynik, fields) as cursor:
        for row in cursor:
            cb = row[0] if row[0] else 0
            co = row[1] if row[1] else 0
            pb = row[2] if row[2] else 0
            po = row[3] if row[3] else 0
            
            #usuniecie pustych kwadratow
            if cb == 0 and co == 0:
                cursor.deleteRow()
            else:
                row[4] = co - cb
                row[5] = po - pb
                cursor.updateRow(row)

    arcpy.management.Delete('memory')
    print(f'SIATKA OK')
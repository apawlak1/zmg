import os
import zipfile

def nested_zip(folder_zrodlowy, folder_docelowy, klucz):
    if not os.path.exists(folder_docelowy):
        os.makedirs(folder_docelowy)

    licznik = 0

    for root, dirs, files in os.walk(folder_zrodlowy):
        for file in files:
            if file.lower().endswith('.zip'):
                sciezka_zip = os.path.join(root, file)
                
                #spr czy w sciezce wystepuje fraza 'OSM' i pobieram 5 pierwszych znakow
                czy_dodac_prefix = 'OSM' in root.upper()
                prefix = file[:5] 
                
                try:
                    with zipfile.ZipFile(sciezka_zip, 'r') as z:
                        for nazwa_wew in z.namelist():
                            czysta_nazwa_pliku = os.path.basename(nazwa_wew)
                            
                            #spr czy klucz jest w nazwie pliku
                            if czysta_nazwa_pliku and klucz.upper() in czysta_nazwa_pliku.upper():
                                nazwa_rdzen, rozszerzenie = os.path.splitext(czysta_nazwa_pliku)
                                
                                if czy_dodac_prefix:
                                    nowa_nazwa = f'{nazwa_rdzen}_{prefix}{rozszerzenie}'
                                else:
                                    nowa_nazwa = czysta_nazwa_pliku
                                
                                with open(os.path.join(folder_docelowy, nowa_nazwa), 'wb') as f_out:
                                    f_out.write(z.read(nazwa_wew))
                                
                                licznik += 1
                except Exception as e:
                    print(f'BLAD')

    print(f'Wypakowano {licznik} plikow do: {folder_docelowy}')
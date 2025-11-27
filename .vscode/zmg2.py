import arcpy
arcpy.env.workspace=r'C:\Users\olaa3\Documents\ArcGIS\Projects\MyProject\ZMG_ola.gdb'
warstwa_pkt='pzgik'

cursor=arcpy.da.SearchCursor(warstwa_pkt, ['SHAPE@X', 'SHAPE@Y'])
for row in cursor:
    print(row)
    ListCoor+=[row[0]+1000, row[1]+2000]
del cursor

nowa_warstwa='pzgik_p'
arcpy.management.CreateFeatureclass(arcpy.env.workspace, nowa_warstwa,\
                                     'POINT', '', 'DISABLED', 'DISABLED',
                                     warstwa_pkt)

cursor=arcpy.da.InsertCursor(nowa_warstwa, ['SHAPE@X', 'SHAPE@Y'])
for coord in ListCoor:
    cursor.insertRow(coord)

del cursor
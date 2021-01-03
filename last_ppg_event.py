#import bibliotek
import arcpy
from math import sqrt, acos, pi, atan, fabs
import pandas as pd
from numpy import array

#zdefiniowanie funkcji
#dlugosc
def segmentLength(x1, y1, x2, y2):
    distance = sqrt(((x2 - x1) ** 2) + ((y2 - y1) ** 2))

    return distance
#azymut
def azimuth(x1, y1, x2, y2):
    try:
        fi = (atan((fabs(x2 - x1)) / (fabs(y2 - y1)))) * 180 / pi
    except ZeroDivisionError:
        fi = 90

    if (x2 - x1) >= 0 and (y2 - y1) > 0:
        azimuth = fi
    elif (x2 - x1) > 0 and (y2 - y1) <= 0:
        azimuth = 180 - fi
    elif (x2 - x1) <= 0 and (y2 - y1) < 0:
        azimuth = 180 + fi
    elif (x2 - x1) < 0 and (y2 - y1) >= 0:
        azimuth = 360 - fi

    return azimuth

#kat wewnetrzny
def angleIn(x1, y1, x2, y2, x3, y3):
    angle =  azimuth(x1, y1, x2, y2) - azimuth(x2, y2, x3, y3) + 180
    if angle < 0:
        return angle + 360
    elif angle > 360:
        return angle - 360
    else:
        return angle

#geometria
def listOfMinimumGeometries(geometry):
    list_of_geometry_type = ['RECTANGLE_BY_AREA', 'RECTANGLE_BY_WIDTH', 'CONVEX_HULL', 'CIRCLE', 'ENVELOPE']
    list_of_minimum_geometries = [arcpy.MinimumBoundingGeometry_management(geometry,  geometry_type+'.shp', geometry_type) for geometry_type in list_of_geometry_type]
    return list_of_minimum_geometries

#zdefiniowanie folderu roboczego oraz danych
arcpy.env.overwriteOutput = 1
arcpy.env.workspace ="C:\pythonpro\egzamin"
workspace = arcpy.env.workspace

inFeatures = "C:\pythonpro\egzamin\dane\BUBD.shp"
outFeatures = "C:\pythonpro\egzamin\dane\BudynekTestowy.shp"

objectField = 'gmlId'
objectID = 'PL.PZGIK.BDOT10k.BUBDA.18.6326392'

where_clause = '"' + objectField + '" = ' + "'" + objectID + "'"

arcpy.Select_analysis(inFeatures, 'Budynek.shp', where_clause)
arcpy.FeatureVerticesToPoints_management('Budynek.shp','Punkty.shp', "ALL")

#utworzenie listy
list = []

# wprowadzeni petli for dla kazdego elementu
for row in arcpy.da.SearchCursor('Punkty.shp', ["FID", "SHAPE@XY"]):
    pointID = row[0]
    pointXY = row[1]
    list.append((pointID, ) + pointXY)
#list = list[:-1]
print (list)
data_list = []

#znalezienie punktow ktore sie powtarzaja
arcpy.management.FindIdentical('Punkty.shp', 'Duplikat.txt', ["SHAPE"], output_record_option='ONLY_DUPLICATES')

list_of_duplicateID = []

with open(workspace + '\Duplikat.txt') as file:
    next(file)
    for line in file:
        row = line.split(';')
        print(row[0])
        list_of_duplicateID.append(int(row[1]))

#lista punktow poczatkoawych i koncowych
list_of_begin_pointID = list_of_duplicateID[0::2]
list_of_end_pointID = list_of_duplicateID[1::2]

print (list_of_begin_pointID)
print (list_of_end_pointID)

index = 0

pointID_end = list[list_of_end_pointID[index]][0]
pointID_begin = list[list_of_begin_pointID[index]][0]

# podzielenie punktow na 3 przypadki:
# 1. wowczas kiedy punkt centralny jest pierwszym punktem
# 2. wowczas kiedy punkt centralny jest ostatnim punktem
# 3. pozostale przypadki
# a) wowczas kiedy punkt centralny bedzie punktem koncowym wieloboku
# b) wowczas kiedy punkt centralnyc bedzie punktem koncowym wieloboku
# c) pozostale przypadki

for point in list:

    #punkt centralny
    pointID_center = point[0]
    X_center = point[1]
    Y_center = point[2]

    print('Punkt centralny: %s' %pointID_center)
#przypadek 1
    if pointID_center == min(array(list)[:, 0]):
        pointID_in = list[list_of_end_pointID[0] - 1][0]
        X_in = list[list_of_end_pointID[0] - 1][1]
        Y_in = list[list_of_end_pointID[0] - 1][2]
        pointID_out = list[list_of_begin_pointID[0] + 1][0]
        X_out = list[list_of_begin_pointID[0] + 1][1]
        Y_out = list[list_of_begin_pointID[0] + 1][2]

        length_in = segmentLength(X_center, Y_center, X_in, Y_in)
        print('%s - %s : %0.3f [m]' % (pointID_in, pointID_center, length_in))
        length_out = segmentLength(X_center, Y_center, X_out, Y_out)
        print('%s - %s : %0.3f [m]' % (pointID_center, pointID_out, length_out))
        angle_in = angleIn(X_in, Y_in, X_center, Y_center, X_out, Y_out)
        print('%s - %s - %s: %0.8f [deg]' %(pointID_in, pointID_center, pointID_out, angle_in))
        print('-------------------------------------------')
#przypadek 3
    elif (pointID_center < max(array(list)[:, 0])) and (pointID_center > min(array(list)[:,0])):
        pointID_out = list[pointID_center + 1][0]
        X_out = list[pointID_center + 1][1]
        Y_out = list[pointID_center + 1][2]
        pointID_in = list[pointID_center - 1][0]
        X_in = list[pointID_center - 1][1]
        Y_in = list[pointID_center - 1][2]
#przypadek 3a
        if pointID_center in list_of_end_pointID:
            length_in = segmentLength(X_in, Y_in, X_center, Y_center)
            print('%s - %s : %0.3f [m]' % (pointID_in, pointID_center, length_in))
            length_out = segmentLength(X_center, Y_center, list[pointID_begin + 1][1], list[pointID_begin + 1][2])
            print('%s - %s : %0.3f [m]' % (pointID_center, pointID_begin + 1, length_out))
            angle_in = angleIn(X_in, Y_in, X_center, Y_center, list[pointID_begin + 1][1], list[pointID_begin + 1][2])
            print('%s - %s - %s: %0.8f [deg]' % (pointID_in, pointID_center, pointID_begin + 1, angle_in))
            print('-------------------------------------------')

            if index < len(list_of_end_pointID)-1:
                index += 1
                pointID_end = list[list_of_end_pointID[index]][0]
                pointID_begin = list[list_of_begin_pointID[index]][0]
#przypadke 3b
        elif pointID_center in list_of_begin_pointID:
            length_in = segmentLength(list[pointID_end - 1][1], list[pointID_end - 1][2], X_center, Y_center)
            print('%s - %s : %0.3f [m]' % (pointID_end - 1, pointID_center, length_in))
            length_out = segmentLength(X_center, Y_center, X_out, Y_out)
            print('%s - %s : %0.3f [m]' % (pointID_center, pointID_out, length_out))
            angle_in = angleIn(list[pointID_end - 1][1], list[pointID_end - 1][2], X_center, Y_center, X_out, Y_out)
            print('%s - %s - %s: %0.8f [deg]' % (pointID_end - 1, pointID_center, pointID_out, angle_in))
            print('-------------------------------------------')
#przypadek 3c
        else:
            length_in = segmentLength(X_in, Y_in, X_center, Y_center)
            print('%s - %s : %0.3f [m]' % (pointID_in, pointID_center, length_in))
            length_out = segmentLength(X_center, Y_center, X_out, Y_out)
            print('%s - %s : %0.3f [m]' % (pointID_center, pointID_out, length_out))
            angle_in = angleIn(X_in, Y_in, X_center, Y_center, X_out, Y_out)
            print('%s - %s - %s: %0.8f [deg]' % (pointID_in, pointID_center, pointID_out, angle_in))
            print('-------------------------------------------')
 #przypadek 2
    else:
        pointID_in = list[pointID_center - 1][0]
        X_in = list[pointID_center - 1][1]
        Y_in = list[pointID_center - 1][2]
        pointID_out = list[list_of_begin_pointID[-1] + 1][0]
        X_out = list[list_of_begin_pointID[-1] + 1][1]
        Y_out = list[list_of_begin_pointID[-1] + 1][2]
        length_in = segmentLength(X_center, Y_center, X_in, Y_in)
        print('%s - %s : %0.3f [m]' % (pointID_in, pointID_center, length_in))
        length_out = segmentLength(X_center, Y_center, X_out, Y_out)
        print('%s - %s : %0.3f [m]' % (pointID_center, pointID_out, length_out))
        angle_in = angleIn(X_in, Y_in, X_center, Y_center, X_out, Y_out)
        print('%s - %s - %s: %0.8f [deg]' %(pointID_in, pointID_center, pointID_out, angle_in))
        print('-------------------------------------------')
    data_list.append([objectID, pointID_center, length_in, length_out, angle_in])


print (data_list)


list = listOfMinimumGeometries('Punkty.shp')

#konwersja poligonow na linie i zapis warstw

for geometry in list:
    near_features = arcpy.FeatureToLine_management(geometry, str(geometry)[:-4] + '_lines.shp', "0.001 Meters", "ATTRIBUTES")
    in_features = 'Punkty.shp'
    # z biblioteki arcpy wykorzystanie funkcji do znalezienia odleglosci do krawedzi poszczegolnych otoczek
    arcpy.Near_analysis(in_features, near_features, location='LOCATION', angle='ANGLE')
    i = 0
    for row in arcpy.da.SearchCursor(in_features, ["NEAR_DIST"]):
        data_list[i].append(row[0])
        i += 1

#nazyw kolumn
column_names = ['ID budynku', 'Numer kolejny wierzcholka', 'Dlugosc segmentu przed [m]', 'Dlugosc segmentu po [m]', 'Kat wewnetrzny [deg]',
                'Strzalka do boku RECTANGLE_BY_AREA [m]', 'Strzalka do boku RECTANGLE_BY_WIDTH [m]', 'Strzalka do boku CONVEX_HULL [m]',
                'Strzalka do boku CIRCLE [m]', 'Strzalka do boku ENVELOPE [m]']

#folder z plikiem wynikowym
output_folder = "C:\pythonpro\egzamin"
output = output_folder + '\\results.csv'

#utworzenie DataFrame z wynikiem i jego eksport do pliku wyjsciowego
Data_Frame = pd.DataFrame(data_list, columns=column_names)
Data_Frame.to_csv('results.csv', index=False, float_format='%.3f')
print (Data_Frame)
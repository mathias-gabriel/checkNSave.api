#! /usr/bin/env python
#-*-coding:utf-8-*-

import shapefile, csv
from urllib.request import urlopen

def getWKT_PRJ (epsg_code):
    import urllib
    wkt = urlopen("http://spatialreference.org/ref/epsg/{0}/prettywkt/".format(epsg_code))
    remove_spaces = wkt.read().decode('utf-8').replace(" ","")
    output = remove_spaces.replace("\n", "")
    return output

trees_shp = shapefile.Writer(shapefile.POINT)

trees_shp.autoBalance = 1
trees_shp.field("nom", "C")
trees_shp.field("adress", "C")
trees_shp.field("cp", "C")
trees_shp.field("ville", "C")
trees_shp.field("categorie", "C")
trees_shp.field("type", "C")
trees_shp.field("tel", "C")
trees_shp.field("description", "C")
trees_shp.field("nbr", "C")
trees_shp.field("dateCreation", "C")


with open("gisdata/142 Défibrillateurs-Paris-Issy.csv",  "rb") as csvfile:

    content = csvfile.readlines()

    counter = 1
    for line in content:
        #print(line)
        if counter > 1:
            row = str(line).split(";")
            print(row)
            nom = row[0]
            adress = row[1]
            cp = row[2]
            ville = row[3]
            latitude = row[4]
            longitude = row[5]
            categorie = row[6]
            type = row[7]
            tel = row[8]
            description = row[9]
            nbr= row[10]
            dateCreation= row[11]

            # create the point geometry
            trees_shp.point(float(longitude),float(latitude))
            # add attribute data
            trees_shp.record(nom, adress, cp, ville, categorie, type,tel, description, nbr, dateCreation)

            print("Feature " + str(counter) + " added to Shapefile.")

        counter = counter + 1

    # save the Shapefile
    trees_shp.save("gisdata/defibrillateurs")

    # create a projection file
    prj = open("gisdata/defibrillateurs.prj", "w")
    epsg = getWKT_PRJ("4326")
    prj.write(epsg)
    prj.close()


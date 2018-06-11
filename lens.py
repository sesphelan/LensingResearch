import sys
import numpy as np
import csv
import math

max_distance = 15 #in arcsecs
reuseCtr = 0
galaxies = []
targets = []

file_name = ""

if len(sys.argv) > 1: # can use any csv file, just make sure file name is included as FIRST argument (with file type)
    file_name = sys.argv[1]
else:
    file_name = "Classes.csv"


# define class for astro-objects
class astrObj():
    def __init__(self, iD, ra, dec, z):
        self.iD = iD
        self.ra = float(ra)
        self.dec = float(dec)
        self.z = float(z)

def degreeToArcSec(ra1, ra2, dec1, dec2):
   #convert all coordinates to radians
   
   ra1 = math.radians(ra1)
   ra2 = math.radians(ra2)
   dec1 = math.radians(dec1)
   dec2 = math.radians(dec2)

   #calculate theta based on equation listed at https://physics.stackexchange.com/questions/224950/how-can-i-convert-right-ascension-and-declination-to-distances
   #cos(theta) = sin(phi)sin(gamma) + cos(phi)cos(gamma)sin(beta-alpha)
   
   theta = math.acos(math.sin(dec1)*math.sin(dec2) + math.cos(dec1)*math.cos(dec2)*math.cos(ra1-ra2))
   #theta = math.acos(cos) #calculates theta

   #convert back to degrees
   theta = math.degrees(theta)
   #return in arcsecs
   theta *= 3600

   return theta      


with open('./'+file_name) as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    for row in readCSV:   
    	if (reuseCtr!=0):
            obj = astrObj(row[0], row[1], row[2], row[3])
            if row[4] == 'GALAXY': #store all Galaxies in a separate array
                galaxies.append(obj)
            else:
                targets.append(obj) 
    	reuseCtr+=1

queries = open("Queries.txt","w") 

queries.seek(0)
queries.truncate() # empty file before writing

# go through each galaxy
potentials = []

# go through each galaxy
#for g in galaxies:
g = galaxies[0]
#search through all non-galaxies
for tar in targets:
    dist = degreeToArcSec(g.ra, tar.ra, g.dec, tar.dec)
    print(dist)
    if dist <= max_distance and g.z == tar.z: #if in the neighborhood of 15 arcs or less
        potentials.append(tar)

queries.close()

print("donezo")



  
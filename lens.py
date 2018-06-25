import sys
import numpy as np
import csv
import math

max_distance = 15 #in arcsecs, radius of light sources around galaxy
reuseCtr = 0
galaxies = [] #holds all galaxies
targets = [] #holds everything

file_name = ""

if len(sys.argv) > 1: # can use any csv file, just make sure file name is included as FIRST argument (with file type)
    file_name = sys.argv[1]
else: # if no argument, use Classes.csv file as default
    file_name = "Top5000.csv"


# define class for astro-objects
class astrObj():
    def __init__(self, iD, ra, dec, z, objType):
        self.iD = iD
        self.ra = float(ra)
        self.dec = float(dec)
        self.z = round(float(z), 4)
        self.type = objType
        self.gID = ""

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
            obj = astrObj(row[0], row[1], row[2], row[3], row[4])
            if row[4] == 'GALAXY': #store all Galaxies in a separate array
                galaxies.append(obj)
            #else:
            targets.append(obj) 
    	reuseCtr+=1

queries = open("Queries.txt","w") 

queries.seek(0)
queries.truncate() # empty file before writing

lenses = []

# go through each galaxy
for g in galaxies:
  #search through all light sources
  potentials = [] #lensing candidates
  for tar in targets:
    if tar.iD == g.iD: # make sure target does not equal galaxy
      continue
    else:
      dist = degreeToArcSec(g.ra, tar.ra, g.dec, tar.dec)
      if dist <= max_distance and dist >= 0: #if in the neighborhood of 15 arcs or less AND positive
        if tar.z == g.z: # if same red shift as galaxy
          if tar not in lenses:
            tar.gID = g.iD
            lenses.append(tar) # IS a lense
          if g not in lenses:
            g.gID = g.iD
            lenses.append(g)
        else:
          potentials.append(tar) # find all light sources that are farther from earth than neighboring galaxy
  '''
  if len(potentials) > 0:
    for i in range(0, len(potentials)):
      print(str(i+1) + ": " + "Potential: " + str(potentials[i].iD) + " Galaxy: " + str(g.iD))
    print("\n")'''
  
  # see if any of these light sources have the same red shift
  for i in range(0, len(potentials)):
    for j in range(i+1, len(potentials)):
      if potentials[i].z == potentials[j].z: # if so, its a lensing incident
        if potentials[i] not in lenses: # only add to list if not alreaday there
          potentials[i].gID = g.iD
          lenses.append(potentials[i])
        if potentials[j] not in lenses:
          potentials[j].gID = g.iD
          lenses.append(potentials[j])

queries.close()

#print out lensing incidents
for l in lenses:
  print("ID: " + str(l.iD) + " Type: " + l.type + " Galaxy ID: " + l.gID)
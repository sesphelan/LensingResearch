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

prefix = file_name.split(".")[0]


# define class for astro-objects
class astrObj():
    def __init__(self, iD, ra, dec, z, objType):
        self.iD = iD
        self.ra = float(ra)
        self.dec = float(dec)
        self.z = round(float(z), 2)
        self.type = objType
        self.passed = False

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
            else: # store all non-galaxies in targets
              targets.append(obj) 
    	reuseCtr+=1

queries = open("Queries.txt","w") 

lenses = []

# go through each galaxy
for g in galaxies:
  #search through all light sources
  potentials = [] #lensing candidates
  for tar in targets:
    
    dist = degreeToArcSec(g.ra, tar.ra, g.dec, tar.dec)
    if dist <= max_distance and tar.z > g.z: #if in the neighborhood of 15 arcs or less AND greater red shift
      potentials.append(tar) # find all light sources that are farther from earth than neighboring galaxy
  
  # see if any of these light sources have the same red shift
  for i in range(0, len(potentials)):
    tempList = []
    tempList.append(g)
    for j in range(i+1, len(potentials)):
      if potentials[i].z == potentials[j].z and potentials[i].passed == False: # if so, its a lensing incident
        if len(tempList) == 1: # only add to list if not alreaday there
          tempList.append(potentials[i])
        tempList.append(potentials[j])
        potentials[j].passed = True
    if len(tempList) > 1:
      lenses.append(tempList)

#print out lensing incidents
#counter = 0
secCounter = 0
for l in lenses:
  counter = 0
  for i in range(0, len(l)):
    if i == 0:
      print("LENSE -- ID: " + str(l[i].iD))
    else:
      print("LENSED OBJECT -- ID: " + str(l[i].iD) + " -- Type: " + l[i].type + " -- Z: " + str(l[i].z))

    
    if counter == 0:
      # add to myDB on CasJobs
      queries.write("casjobs run 'SELECT ALL specObjID,ra,dec,z,class INTO mydb.Models_" + prefix + "_" + str(secCounter) + " FROM SpecObj where specObjID="+str(l[i].iD)+"'" + "\n\n")
    else:
      queries.write("casjobs run 'INSERT INTO mydb.Models_" + prefix + "_" + str(secCounter) + " SELECT ALL specObjID,ra,dec,z,class FROM SpecObj where specObjID="+str(l[i].iD)+"'" + "\n\n")
    # download table locally'''

    counter += 1
  queries.write("casjobs extract -b Models_" + prefix + "_" + str(secCounter) + " -F -type CSV -d ./Models/\n\n")
  secCounter += 1

#queries.write("casjobs extract -b Models_" + prefix + " -F -type CSV -d ./Models/\n\n")
queries.close()

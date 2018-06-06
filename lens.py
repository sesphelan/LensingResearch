import sys
import numpy as np
import csv
import math

#WIGGLE_ROOM=0.0042 # standard is 0.0041 but ill allow for a little bit extra
max_distance = 15
reuseCtr = 0
galaxies = []
targets = []

file_name = ""
only_galaxies = False

if len(sys.argv) > 1: # can use any csv file, just make sure file name is included as FIRST argument (with file type)
    file_name = sys.argv[1]
else:
    file_name = "Classes.csv"

if len(sys.argv) > 2 and sys.argv[2] == "True":
    only_galaxies = True

# define class for astro-objects
class astrObj():
    def __init__(self, iD, ra, dec, z):
        self.iD = iD
        self.ra = float(ra)
        self.dec = float(dec)
        self.z = float(z)

def degreeToArcSec(ra1, ra2, dec1, dec2):
    deltaRA = ra1 - ra2
    deltaDec = dec1 - dec2

    # adjust value of deltaRA for change in longitude
    # see http://spiff.rit.edu/classes/phys445/lectures/astrom/astrom.html for explanation
    avgDec = (dec1 + dec2) / 2
    deltaRA = deltaRA * math.cos(avgDec)
    # convert to arcsecs
    deltaRA *= 3600
    deltaDec *= 3600

    #final result using quadratic formula
    res = math.sqrt(math.pow(deltaRA, 2) + math.pow(deltaDec, 2))
    return res


with open('./'+file_name) as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    for row in readCSV:   
    	if (reuseCtr!=0):
            obj = astrObj(row[0], row[1], row[2], row[3])
            if only_galaxies = False:
                if row[4] == 'GALAXY': #store all Galaxies in a separate array
                    galaxies.append(obj)
                else:
                    targets.append(obj) 
            else:
                galaxies.append(obj)
    	reuseCtr+=1

queries = open("Queries.txt","w") 

queries.seek(0)
queries.truncate() # empty file before writing

# go through each galaxy
for g in galaxies:
    #search through all non-galaxies
    potentials = []
    for tar in targets:
        dist = degreeToArcSec(g.ra, tar.ra, g.dec, tar.dec)
        print(dist)
        if dist <= max_distance and g.z == tar.z: #if in the neighborhood of 15 arcs or less AND red shift is the same
            potentials.append(tar)

counter = 1;
for i in potentials:
	
	queries.write("casjobs run 'SELECT ALL p.objid,p.ra,p.dec,pz.z INTO mydb.object_"+str(counter)+" FROM SpecObj AS p JOIN Photoz AS pz ON pz.objid = p.objid where p.z=" + str(i.z)"'\n\n")
	# and now to download table:
	#queries.write("casjobs extract -b object_"+str(i)+" -F -type CSV -d ./Models/\n\n")
	# and now to drop table remotely:
	#queries.write("java -jar casjobs.jar execute -t 'mydb/2' 'drop table object_"+str(i)+"'\n\n")
    counter++;

queries.close()

print("donezo")

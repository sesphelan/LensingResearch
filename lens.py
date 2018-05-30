import sys
import numpy as np
import csv
import math

#WIGGLE_ROOM=0.0042 # standard is 0.0041 but ill allow for a little bit extra
max_distance = 15

reuseCtr = 0;

galaxies = []
targets = []

# define class for astro-objects
class astrObj():
    def __init__(self, iD, ra, dec, z):
        self.iD = iD
        self.ra = ra
        self.dec = dec
        self.z = z

def degreeToArcSec(ra1, ra2, dec1, dec2):
    deltaRA = ra1 - ra2
    dletaDec = dec1 - dec2

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


with open('./Classes.csv') as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    for row in readCSV:   
    	if (reuseCtr!=0):
            obj = astrObj(row[0], row[1], row[2], row[3])
            if row[4] == 'GALAXY': #store all Galaxies in a separate array
                galaxies.append(obj)
            else:
                targets.append(obj)
    	reuseCtr+=1

    # go through each galaxy
    for g in galaxies:
        #search through all non-galaxies
        potentials = []
        for tar in targets:
            dist = degreeToArcSec(g.ra, tar.ra, g.dec, tar.dec)
            if dist <= max_distance and g.z == tar.z: #if in the neighborhood of 15 arcs or less
                potentials.append(tar)

        
'''
queries = open("Queries.txt","w") 

queries.seek(0)
queries.truncate() # empty file before writing

for i in num:
	ratop = ra[i]+size[i]  #Defining rectangle of interest 
	rabot = ra[i]-size[i]
	dectop = dec[i]+size[i]
	decbot = dec[i]-size[i]
	queries.write("java -jar casjobs.jar run 'SELECT ALL p.objid,p.ra,p.dec,pz.z INTO mydb.object_"+str(i)+" FROM PhotoObj AS p JOIN Photoz AS pz ON pz.objid = p.objid where p.ra between "+str(rabot)+" and "+str(ratop)+" and p.dec between "+str(decbot)+" and "+str(dectop)+"' \n\n")
	# and now to download table:
	queries.write("java -jar casjobs.jar extract -b object_"+str(i)+" -F -type CSV -d ./Models/\n\n")
	# and now to drop table remotely:
	#queries.write("java -jar casjobs.jar execute -t 'mydb/2' 'drop table object_"+str(i)+"'\n\n")

queries.close()
'''
print("donezo")

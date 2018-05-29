import sys
import numpy as np
import csv

#WIGGLE_ROOM=0.0042 # standard is 0.0041 but ill allow for a little bit extra
max_distance = 15

reuseCtr = 0;
objID = []
ra = []
dec = []
lensz = []

with open('./Classes.csv') as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    for row in readCSV:
    	if (reuseCtr!=0):
    		objID.append(row[1])
    		ra.append(row[2])
    		dec.append(row[3])
    		lensz.append(row[4])
    		
            '''
    		rdata = row[5].split(':')
    		rconv = float(rdata[0])*15.+float(rdata[1])*0.25+float(rdata[2])*0.00416667
    		ra.append(rconv)

    		ddata = row[6].split(':')
    		negative = 0
    		if(ddata[0][0]=='-'):
    			ddata[0] = -1.*float(ddata[0])
    			negative = 1
    		dconv = float(ddata[0]) + float(ddata[1])/60. + float(ddata[2])/3600
    		if (negative==1):
    			dconv = -1.*dconv
    		dec.append(dconv)

    		mags.append(row[7])
    		magl.append(row[8])
    		Nim.append(row[9])
    		size.append(float(row[10])*WIGGLE_ROOM) #convert from arcseconds to degrees (with extra wiggle room)
            '''
    	reuseCtr+=1


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

print("donezo")

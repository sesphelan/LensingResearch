import sys

if len(sys.argv) > 1: # can use any csv file, just make sure file name is included as FIRST argument (with file type)
    file_name = sys.argv[1]
else: # if no argument, use Classes.csv file as default
    file_name = "CrossTest.txt"

prefix = file_name.split(".")[0]

with open('./'+file_name, 'r') as myfile:
	data = myfile.read().splitlines()
	firstLine = data[1].split(',')
	minRA = float(firstLine[1])
	maxRA = float(firstLine[1])
	minDec = float(firstLine[2])
	maxDec = float(firstLine[2])
	for i in range(2, len(data)):

		line = data[i].split(',')

		if float(line[1]) <= float(minRA):
			minRA = line[1]
		elif float(line[1]) >= float(maxRA):
			maxRA = line[1]
		if float(line[2]) <= float(minDec):
			minDec = line[2]
		elif float(line[2]) >= float(maxDec):
			maxDec = line[2]

	print("min RA: " + str(minRA))
	print("max RA: " + str(maxRA))
	print("min Dec: " + str(minDec))
	print("max Dec: " + str(maxDec))
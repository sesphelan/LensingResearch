import sys

from FindMinMax import FindMinMax

if len(sys.argv) > 1: # can use any csv file, just make sure file name is included as FIRST argument (with file type)
    file_name = sys.argv[1]
else: # if no argument, use Classes.csv file as default
    file_name = "CrossTest.txt"

prefix = file_name.split(".")[0]

if len(sys.argv) > 2:
	number = int(sys.argv[2])
else:
	number = 5

files = [] # holds all files created by script
partitions = []

for i in range(0, number):
	f = open(prefix + "_" + str(i), "w+")
	f.write("specObjID,ra,dec,z,class\n")
	files.append(f)

with open('./'+file_name, 'r') as myfile:
	data = myfile.read().splitlines()
	maxRA = float(data[1].split(',')[1])
	minRA = float(data[1].split(',')[0])

	interval = (maxRA-minRA) / float(number)

	current = minRA

	for i in range(0, number):
		tempList = []
		for j in range(2, len(data)):

			line = data[j]

			ra = float(data[j].split(',')[1])
			if ra >= current and ra < current + interval:
				tempList.append(line)
			if i == number-1 and j == len(data) -1:
				tempList.append(line)	

		partitions.append(tempList)
		current += interval

for i in range(0, number):
	f = files[i]
	for j in range(0, len(partitions[i])):
		f.write(partitions[i][j] + "\n")
	f.close()

for i in range(0, number):
	name = prefix + "_" + str(i)
	arr = FindMinMax(name)
	if len(arr) > 0:
		f = open(name, "r")
		data = f.readlines()
		data[0] = "specObjID,ra,dec,z,class\n" + str(arr[0]) + "," + str(arr[1]) + "," + str(arr[2]) + "," + str(arr[3]) + "\n"
		with open(name, "w") as file:
			file.writelines(data)



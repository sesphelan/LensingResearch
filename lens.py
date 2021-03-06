import sys
import numpy as np
import csv
import math
import threading

from element import Element
from executionengine import Relation, Relations, Plan
from node import Node
from quadtree import QuadTree
from query import Query
from util import EucDist, compute_level
from voxel import Voxel

max_distance = 15 #in arcsecs, radius of light sources around galaxy
reuseCtr = 0
galaxies = [] #holds all galaxies
targets = [] #holds everything

file_name = ""

if len(sys.argv) > 1: # can use any csv file, just make sure file name is included as FIRST argument (with file type)
    file_name = sys.argv[1]
else: # if no argument, use Classes.csv file as default
    file_name = "CrossTest.txt"

prefix = file_name.split(".")[0]


# define class for astro-objects
class astrObj():
    def __init__(self, iD, ra, dec, z, objType):
        self.iD = iD
        self.ra = float(ra)
        self.dec = float(dec)
        self.z = round(float(z), 2) + 0
        self.type = objType # galaxy, QSO, or star
        self.passed = False #boolean used in parsing objects

'''
Returns standard Quadtree using an array of strings generated from the
input text file. 

text input: array of strings holding entire input file
  each element holds a line of text

output: quadtree with all nodes created, structured
'''
def build_tree(text):
    #query = query_broadcast.value

    root = None
    geometric_centroid_ra = geometric_centroid_dec = None
    centroid = None
    cent_min_dist = float("inf")
    voxel = None
    for i in range(1, len(text)): # skip first line
        #for line in lines[1].split("\n"):
        split = text[i].split(",")
        if len(split) == 4:
            min_ra, max_ra, min_dec, max_dec = split
            voxel = Voxel(float(min_ra), float(max_ra), float(min_dec), float(max_dec))
            geometric_centroid_ra, geometric_centroid_dec = voxel.getVoxelCentroid()
            root = Node(voxel)
        elif text[i]:

            star = Element(int(split[0]), float(split[1]), float(split[2]), float(split[3]), 0, split[4])

            root.addElement(star)

            dist = EucDist(star.getRa(), geometric_centroid_ra, star.getDec(), geometric_centroid_dec)
            if dist < cent_min_dist:
                centroid = star
                cent_min_dist = dist

    root.setSize(len(root.getElements()))
    root.addCentroid(centroid)

    level = compute_level(voxel.getSideSize(), voxel.getHeightSize(), 0.00416667)
    tree = QuadTree(root, level)
    
    return tree  

# basic MergeSort code taken from https://www.geeksforgeeks.org/merge-sort/
# sorts by red shift attribute in object
# takes in array to work on, lower and upper bounds 
# all inputs come from mergeSort() function below
# no output
def merge(arr, l, m, r):
    n1 = m - l + 1
    n2 = r- m
 
    # create temp arrays
    L = [0] * (n1)
    R = [0] * (n2)
 
    # Copy data to temp arrays L[] and R[]
    for i in range(0 , n1):
        L[i] = arr[l + i]
 
    for j in range(0 , n2):
        R[j] = arr[m + 1 + j]
 
    # Merge the temp arrays back into arr[l..r]
    i = 0     # Initial index of first subarray
    j = 0     # Initial index of second subarray
    k = l     # Initial index of merged subarray
 
    while i < n1 and j < n2 :
        if L[i].z <= R[j].z:
            arr[k] = L[i]
            i += 1
        else:
            arr[k] = R[j]
            j += 1
        k += 1
 
    # Copy the remaining elements of L[], if there
    # are any
    while i < n1:
        arr[k] = L[i]
        i += 1
        k += 1
 
    # Copy the remaining elements of R[], if there
    # are any
    while j < n2:
        arr[k] = R[j]
        j += 1
        k += 1
 
# l is for left index and r is right index of the
# sub-array of arr to be sorted
# does NOT return an array, works on array passed in
def mergeSort(arr,l,r):
    if l < r:
 
        # Same as (l+r)/2, but avoids overflow for
        # large l and h
        m = (l+(r-1))/2
 
        # Sort first and second halves
        mergeSort(arr, l, m)
        mergeSort(arr, m+1, r)
        merge(arr, l, m, r)

# MAIN function of program (no return value)
# takes only string of input file name
# prints results of query to std output and generates series of queries
# to be run with command line CAS tool
def run(file_name):
  with open('./'+file_name, 'r') as myfile:
    data = myfile.read().splitlines() # create string list from txt file

    tree = build_tree(data) #build tree with it
    root = tree.root

    queries = open("Queries.txt","w") # file that stores all queries
    lenses = []

    for node in tree.nodes:
      if node.getType() == "3": #only run neighboring query on galaxies
        neighbors = tree.find_neighbors(node, root, 0.00416667, []) # 15 arcsec limit
        mergeSort(neighbors, 0, len(neighbors)-1) # mergesort for efficiency of finding neighbors
        
        i = 0 # find all lensing incidents by parsing Neighbors
        while( i < len(neighbors)):
          tempList = []
          tempList.append(node.getElements()[0])
          target = neighbors[i]
          count = i
          while(target.z == neighbors[i].z): # same red shift needed
            if target.getType() != "3":
              tempList.append(target)
            count += 1
            if count < len(neighbors):
              target = neighbors[count]
            else:
              break
          if len(tempList) > 3: # need at least 3 for a lensing incident
            lenses.append(tempList)
          i = count
    counter = 0
    for l in lenses: # print to console
      for i in range(0, len(l)):
        if i == 0:
          print("LENSE -- ID: " + str(l[i].pointId))
        else:
          print("LENSED OBJECT -- ID: " + str(l[i].pointId) + " -- Type: " + l[i].astroType + " -- Z: " + str(l[i].z))

        if counter == 0:
        # add to myDB on CasJobs
          queries.write("casjobs run 'SELECT ALL objID,ra,dec,z,type INTO mydb.Models_" + prefix + " FROM PhotoObj where objID="+str(l[i].pointId)+"'" + "\n\n")
        else:
          queries.write("casjobs run 'INSERT INTO mydb.Models_" + prefix + " SELECT ALL objID,ra,dec,z,type FROM PhotoObj where objID="+str(l[i].pointId)+"'" + "\n\n")
      # download table locally
        counter += 1



    queries.write("casjobs extract -b Models_" + prefix + " -F -type CSV -d ./Models/\n\n")
    

run(file_name) # run MAIN function

#  FOR THREADING PURPOSES, UNCOMMENT lines below

'''
for i in range(4):
  t = threading.Thread(target=run, args=(prefix + "_partition_" + str(i),))
  t.start()
'''
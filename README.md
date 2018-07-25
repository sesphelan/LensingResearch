# LensingResearch

Constellation Queries Project under Dennis Shasha.
Goal: Identify lensing incidents by finding galaxies and looking within 15 arcseconds away for light sources with the same red shift.

How to run:

Simply run with the command: "python lens.py" to run script on the default txt file titled CrossTest.txt.

If a different txt file wants to be used, ensure that this file matches the exact schema of the CrossTest.txt file, and include the name of the file
as a command line argument (i.e. run "python lens.py TopMillion.txt" to run the script on a file titled TopMillion.txt). The schema for the CrossTest.txt file
only includes specObjID, ra, dec, z, and class (in that exact order) with a comma as a delimiter.

It is also important to note that the second line of the txt file must contain only four values: the minimum RA of the data set, the max RA, min dec, and max dec.

Explanation of code:

First, I create a QuadTree out of each object in the txt file using the build_tree function (modified from the files given to me by Fabio). Then, I traverse
each node in the tree, and run a neighbors query on each galaxy that returns all non-galaxies at most 15 arcseconds away from it in a list titled Neighbors.
I run a merge sort on Neighbors to order the potential lensing incidents by red shift. Then, I pick out any stars that share the same redshift with at least
two other stars, thus indicating a lensing incident. I return all lensing incidents in a List of lists titled Lenses, where each List begins with the lensing galaxy,
and all subsequent elements are the lensing incidents that share the same red shift value.

I print the Lenses list to standard output when all parsing has finished. I also create a list of queries in 
a text file titled "Queries.txt" (does not need to be created before first run). Once the script finishes, copy and paste all of the contents in this text
file into the terminal to create an object in the "mydb" remotely, as well as to create an object locally in a folder titled "Models." All lensing incidents
will be stored in a single csv file.
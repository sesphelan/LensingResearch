# LensingResearch

Constellation Queries Project under Dennis Shasha.
Goal: Identify lensing incidents by finding galaxies and looking within 15 arcseconds away for light sources with the same red shift.

How to run:

Simply run with the command: "python lens.py" to run script on the default csv file titled Top5000.csv, which contains the first 5000 rows of the
catalog.

If a different csv file wants to be used, ensure that this file matches the exact schema of the Top500.csv file, and include the name of the file
as a command line argument (i.e. run "python lens.py TopMillion.csv" to run the script on a file titled TopMillion.csv). The schema for the Top500.csv file
only includes specObjID, ra, dec, z, and class (in that exact order) with a comma as the delimiter.

Explanation of code:

First, I parse the csv file and put all of the galaxies into a List. Then, I parse through the galaxies and run a function
called degreeToArcSec() to calculate the angular distance in arcseconds between each galaxy and each other object in the catalog. If an object
is less than 15 arcseconds away, I place it in a separate list called Potentials.

Finally, I look at the Potentials list and see if any of the objects neighbor the same galaxy (and are both farther from earth than the galaxy),
as well as have the same red shift data (up to 4 decimal places). If they do, these objects are lensing incidents and I place them in a final list titled Lenses.

After all the parsing finishes, I print to standard output the object ID of each lensing incident and the type of object.
from element import Element
from executionengine import Relation, Relations, Plan
from node import Node
from quadtree import QuadTree
from query import Query
from util import EucDist, compute_level
from voxel import Voxel

def build_tree(text):
    #query = query_broadcast.value

    root = None
    geometric_centroid_ra = geometric_centroid_dec = None
    centroid = None
    cent_min_dist = float("inf")
    voxel = None
    for i in range(1, len(text)):
        #for line in lines[1].split("\n"):
        split = text[i].split(",")
        if len(split) == 4:
            min_ra, max_ra, min_dec, max_dec = split
            voxel = Voxel(float(min_ra), float(max_ra), float(min_dec), float(max_dec))
            geometric_centroid_ra, geometric_centroid_dec = voxel.getVoxelCentroid()
            root = Node(voxel)
        elif text[i]:
            #border = False if  split[5].lower() == "false" else True
            
            '''
            star = Element(int(split[0]), float(split[1]), float(split[2]), float(split[3]), float(split[4]),
                           float(split[5]), float(split[6]), float(split[7]), float(split[8]),
                           float(split[9]), float(split[10]), float(split[11]), float(split[12]), 0, border)'''

            star = Element(int(split[0]), float(split[1]), float(split[2]), float(split[3]), 0)

            root.addElement(star)

            dist = EucDist(star.getRa(), geometric_centroid_ra, star.getDec(), geometric_centroid_dec)
            if dist < cent_min_dist:
                centroid = star
                cent_min_dist = dist

    root.setSize(len(root.getElements()))
    root.addCentroid(centroid)

    level = compute_level(voxel.getSideSize(), voxel.getHeightSize(), 0.00416667)
    tree = QuadTree(root, level)

    print("\n**** Data Descriptions *****")
    print("Sky Voxel: %s,%s,%s,%s" % (voxel.x_left, voxel.x_right, voxel.y_left, voxel.y_right))
    print("Sky Diagonal: %s" % voxel.getDiagonal())
    print("Tree Level: %s" % level)
    print("Tree Elements: %s" % root.size)
    print("Tree Leaf nodes: %s" % len(tree.nodes))
    print("**** End Data Descriptions *****\n")

    return tree


with open('CrossTest.txt', 'r') as myfile:
	data = myfile.readlines()
	for i in range(0, len(data)):
		data[i] = data[i].rstrip()
	tree = build_tree(data)
	root = tree.root
	for node in tree.nodes:
		'''neighbors = tree.find_neighbors(node, root, 0.00416667, [])
		if len(neighbors) > 0:
			print(neighbors)'''
		print("hi")



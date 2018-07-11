from collections import defaultdict
from os import path
from sys import argv
from time import time

from pyspark import SparkConf, SparkContext

from element import Element
from executionengine import Relation, Relations, Plan
from node import Node
from quadtree import QuadTree
from query import Query
from util import EucDist, compute_level
from voxel import Voxel


def build_tree(text):
    query = query_broadcast.value

    root = None
    geometric_centroid_ra = geometric_centroid_dec = None
    centroid = None
    cent_min_dist = float("inf")
    voxel = None
    for lines in text:
        for line in lines[1].split("\n"):
            split = line.split(",")
            if len(split) == 4:
                min_ra, max_ra, min_dec, max_dec = split
                voxel = Voxel(float(min_ra), float(max_ra), float(min_dec), float(max_dec))
                geometric_centroid_ra, geometric_centroid_dec = voxel.getVoxelCentroid()
                root = Node(voxel)
            elif line:
                border = False if split[13].lower() == "false" else True

                '''star = Element(int(split[0]), float(split[1]), float(split[2]), float(split[3]), float(split[4]),
                               float(split[5]), float(split[6]), float(split[7]), float(split[8]),
                               float(split[9]), float(split[10]), float(split[11]), float(split[12]), 0, border)'''

                star = Element(int(split[0]), float(split[1]), float(split[2]), float(split[3]), 0, border)

                root.addElement(star)

                if star.border is False:
                    dist = EucDist(star.getRa(), geometric_centroid_ra, star.getDec(), geometric_centroid_dec)
                    if dist < cent_min_dist:
                        centroid = star
                        cent_min_dist = dist

    root.setSize(len(root.getElements()))
    root.addCentroid(centroid)

    level = compute_level(voxel.getSideSize(), voxel.getHeightSize(), query.getMaxDistance())
    tree = QuadTree(root, level)

    print("\n**** Data Descriptions *****")
    print("Sky Voxel: %s,%s,%s,%s" % (voxel.x_left, voxel.x_right, voxel.y_left, voxel.y_right))
    print("Sky Diagonal: %s" % voxel.getDiagonal())
    print("Tree Level: %s" % level)
    print("Tree Elements: %s" % root.size)
    print("Tree Leaf nodes: %s" % len(tree.nodes))
    print("**** End Data Descriptions *****\n")

    return [tree]


def produce_candidates_color(tree):
    query = query_broadcast.value
    query_elements = query.getQuery()
    query_anchor_id = query.getAnchor().getId()
    query_max_dist = query.getMaxDistance()
    epsilon = query.getEpsilon() * query_max_dist
    query_matrix_distance = query.getDistanceMatrix()

    root = tree.root
    nodes = tree.nodes

    relations = defaultdict(set)
    for node in nodes:
        anchors = node.getElements()
        neighbors = tree.find_neighbors(node, root, query_max_dist + epsilon, [])
        neighbors_size = len(neighbors)

        if neighbors_size > 0:
            for anchor in anchors:
                u_err = anchor.u_err
                g_err = anchor.g_err
                r_err = anchor.r_err
                i_err = anchor.i_err
                z_err = anchor.z_err

                for neighbor in neighbors:
                    if neighbor.pointId != anchor.pointId:

                        if anchor.u - u_err <= neighbor.u <= anchor.u + u_err and \
                                                        anchor.g - g_err <= neighbor.g <= anchor.g + g_err and \
                                                        anchor.r - r_err <= neighbor.r <= anchor.r + r_err and \
                                                        anchor.i - i_err <= neighbor.i <= anchor.i + i_err and \
                                                        anchor.z - z_err <= neighbor.z <= anchor.z + z_err:

                            distance = EucDist(anchor.getRa(), neighbor.getRa(), anchor.getDec(), neighbor.getDec())

                            for e in query_elements:
                                eid = e.getId()
                                if eid != query_anchor_id:
                                    query_distance = query_matrix_distance[query_anchor_id][eid]

                                    if query_distance - epsilon <= distance <= query_distance + epsilon:
                                        relations[anchor.pointId].add((anchor, neighbor, eid))

        node.visited = True
    return relations.values()


def produce_candidates_no_color(tree):
    query = query_broadcast.value
    query_elements = query.getQuery()
    query_anchor_id = query.getAnchor().getId()
    query_max_dist = query.getMaxDistance()
    epsilon = query.getEpsilon() * query_max_dist
    query_matrix_distance = query.getDistanceMatrix()

    root = tree.root
    nodes = tree.nodes

    relations = defaultdict(set)
    for node in nodes:
        anchors = node.getElements()
        neighbors = tree.find_neighbors(node, root, query_max_dist + epsilon, [])
        neighbors_size = len(neighbors)

        if neighbors_size > 0:
            for anchor in anchors:

                for neighbor in neighbors:

                    if neighbor.pointId != anchor.pointId:
                        distance = EucDist(anchor.getRa(), neighbor.getRa(), anchor.getDec(), neighbor.getDec())

                        for e in query_elements:
                            eid = e.getId()
                            if eid != query_anchor_id:
                                query_distance = query_matrix_distance[query_anchor_id][eid]

                                if query_distance - epsilon <= distance <= query_distance + epsilon:
                                    relations[anchor.pointId].add((anchor, neighbor, eid))

        node.visited = True
    return relations.values()


def prepare_matching_pairs(data):
    query = query_broadcast.value
    query_anchor_id = query.getAnchor().getId()

    dict_rel_id = dict()
    relations = Relations()
    query_l = query.getQuery()

    for q in query_l:
        if q.getId() != query_anchor_id:
            relations.addRelation(Relation(q.getId(), []))
            dict_rel_id[q.getId()] = len(relations.getRelations()) - 1

    for anchor, partner, eid in data:
        id_rel = dict_rel_id[eid]
        relation1 = relations.getRelations()
        relation1[id_rel].addStar(anchor, partner)

    return relations


def filter_candidates(relations):
    query = query_broadcast.value

    filter_operation = True
    ee = Plan(query)
    plan = ee.buildPlan(relations, filter_operation)
    if plan is not None:

        solutionList = []
        totalSolutions = 0
        result = plan.getNext()
        while not result == "end":
            if len(result) > 0:
                solutionList.extend(result)
                print("**************** SOLUTIONS ************")
                while result != "end":
                    for r in result:
                        totalSolutions += 1
                        for i in range(len(r.getStars())):
                            if i == 0:
                                print("Ancor:\tId: %s\tra: %s\tDec: %s" % (r.getStar(i).getId(), r.getStar(i).getRa(),
                                                                           r.getStar(i).getDec()))
                            else:
                                print ("Elem Relation: %s Id: %s Ra: %s Dec:%s" % (r.getMetadataPos(i),
                                                                                   r.getStar(i).getId(),
                                                                                   r.getStar(i).getRa(),
                                                                                   r.getStar(i).getDec()))
                    result = plan.getNext()
                    if result != "end":
                        solutionList.extend(result)
                print("**************** SOLUTIONS ************")
                print("***** Solution Shapes: Total: %s" % totalSolutions)

            else:
                result = plan.getNext()
    else:
        print("No Plan")
    print("End Approx based solution")
    return solutionList


def save_result(solution_list, filename):
    if len(solution_list) > 0:
        with open(filename, "w") as f:
            count = 1
            for solution in solution_list:
                if solution:
                    for r in solution:
                        f.write("Solution = %s\n" % count)
                        for element in r.getStars():
                            f.write("Star = %s\n" % element)
                        f.write("\n")
                        count += 1


if __name__ == '__main__':
    start_time = time()
    if len(argv) < 3:
        print("Pure Constellations Queries:\n[1]InputFile\n[2]OutputFile\n[3]Neighbor Limit")
    else:

        spark_conf = SparkConf()
        spark_conf.setAppName("Isotropic Constellations Queries")
        spark_conf.setMaster("local[1]")  # yarn-client
        # spark_conf.set("spark.executor.instances", "120")
        # spark_conf.set("spark.executor.cores", "1")
        # spark_conf.set("spark.driver.memory","24g")
        # spark_conf.set("spark.executor.memory","4g")
        # spark_conf.set("spark.yarn.queue", "prioridade")

        sc = SparkContext(conf=spark_conf)

        dir_path = path.dirname(path.abspath(__file__))

        sc.addPyFile(dir_path + "/element.py")
        sc.addPyFile(dir_path + "/node.py")
        sc.addPyFile(dir_path + "/quadtree.py")
        sc.addPyFile(dir_path + "/query.py")
        sc.addPyFile(dir_path + "/util.py")
        sc.addPyFile(dir_path + "/voxel.py")
        sc.addPyFile(dir_path + "/executionengine.py")

        # sc.addFile(path.dirname(path.abspath(__file__)), True)
        query = Query.defineQuery(float(argv[3]))

        query_broadcast = sc.broadcast(query)

        text_rdd = sc.newAPIHadoopFile(argv[1], "org.apache.hadoop.mapreduce.lib.input.TextInputFormat",
                                       "org.apache.hadoop.io.Text", "org.apache.hadoop.io.LongWritable",
                                       conf={"textinputformat.record.delimiter": "\n\n"})

        tree_rdd = text_rdd.mapPartitions(build_tree)

        candidates_rdd = tree_rdd.flatMap(produce_candidates_color)

        relations_rdd = candidates_rdd.map(prepare_matching_pairs)

        filter_rdd = relations_rdd.map(filter_candidates)

        result = relations_rdd.collect()
        sc.stop()

        save_result(result, argv[2])

        end_time = time() - start_time
        print("Total Time: %s" % end_time)

from element import Element
from util import EucDist


class Query(object):


    def __init__(self, query, anchor, minDist=0, minDistElement=None, distM=None, epsilon=0.007, approx=True, distributed=False, margin=0, maxDist=0):
        self.query = query
        self.approx = approx
        self.epsilon = epsilon
        self.distributed = distributed
        self.minDistElement = None
        self.minDist = minDist
        self.distances = distM
        self.anchor = anchor
        self.margin = margin
        self.maxDistance = maxDist


    def getQuery(self):
        return self.query


    def getApprox(self):
        return self.approx


    def getSize(self):
        return len(self.query)


    def getEpsilon(self):
        return self.epsilon


    def getDistributed(self):
        return self.distributed


    def getMinDist(self):
        return self.minDist


    def getMinDistElement(self):
        return self.minDistElement


    def getDistanceMatrix(self):
        return self.distances


    def getAnchor(self):
        return self.anchor


    def getMargin(self):
        return self.margin


    def getMaxDistance(self):
        return self.maxDistance


    @staticmethod
    def defineQuery(epsilon, approx=True, distributed=False, margin=0):

        element_list = [
            Element(1, 340.125920709671, 3.35842462611196, 15.88071, 0, 14.94726, 0, 14.25543, 0, 13.81744, 0, 13.52653,
                    0, 0, False),
            Element(2, 340.125919636357, 3.35841548819963, 15.88897, 0, 14.96084, 0, 14.27048, 0, 13.83855, 0, 13.55785,
                    0, 0, False),
            Element(3, 340.125941094769, 3.35841455436284, 15.84727, 0, 14.95589, 0, 14.26131, 0, 13.8294, 0, 13.52057,
                    0, 0, False),
            Element(4, 340.125942982763, 3.3584407242725, 15.98358, 0, 14.94892, 0, 14.26593, 0, 13.8352, 0, 13.5495,
                    0, 0,False)]

        anchorElement = Query.getCentroidFromElementList(element_list)

        print("Query Anchor: %s" % anchorElement.getId())
        print("Query Epsilon: %s"% epsilon)
        qSize = len(element_list)
        minDist = 1000
        maxDist = 0
        minDistElement = None
        distM = [[0 for n in range(qSize + 1)] for m in range(qSize + 1)]
        used = []
        for element in element_list:

            used.append(element)

            if element != anchorElement:

                element.distToCentroid = EucDist(anchorElement.Ra, element.Ra, anchorElement.Dec, element.Dec)
                if element.distToCentroid < minDist:
                    minDistElement = element
                    minDist = element.distToCentroid

            element_list_comp = list(set(element_list) - set(used))

            for elementj in element_list_comp:
                dist = EucDist(element.Ra, elementj.Ra, element.Dec, elementj.Dec)
                distM[element.getId()][elementj.getId()] = dist
                distM[elementj.getId()][element.getId()] = dist
                if dist > maxDist:
                    maxDist = dist

            print("Distance to query centroid: queryid %s dist %s" % (element.getId(), element.distToCentroid))
        print ("*************** Matrix **************")
        for i in range(qSize + 1):
            for j in range(qSize + 1):
                print ("Posicao i: %s j: %s Val: %s" % (i,j,distM[i][j]))
        print("*************** End Matrix ***************")
        # Compute pairwise distances

        # #order the query points
        element_list.sort(key=lambda elements: elements.distToCentroid)
        # minimum distance is in the second element. First is zero

        queryDefinition = Query(element_list, anchorElement, minDist, minDistElement, distM, epsilon, approx, distributed, margin, maxDist)

        return queryDefinition


    @staticmethod
    def getCentroidFromElementList(element_list):
        qSize = len(element_list)

        avg_Ra = 0
        avg_Dec = 0
        for element in element_list:
            avg_Ra += element.Ra
            avg_Dec += element.Dec

        avg_Ra /= qSize
        avg_Dec /= qSize

        # #Find the nearest query point as the centroid
        min_dist = 100000
        tmp_dist = 0
        centroid = None

        for element in element_list:
            tmp_dist = EucDist(element.Ra, avg_Ra, element.Dec, avg_Dec)
            if tmp_dist < min_dist:
                min_dist = tmp_dist
                centroid = element
                # print ("centroid point is the q" + (str)(centroid_index))
        return centroid

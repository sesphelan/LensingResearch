from util import EucDist


class Tuple(object):
    def __init__(self, stars=[]):
        self.metadata = []
        self.stars = []

    def addTuple(self, tuple):
        self.stars.extend(tuple.getStars())
        self.metadata.extend(tuple.getMetadata())

    def addStar(self, s, rel):
        self.stars.append(s)
        self.metadata.append(rel)

    def getMetadataPos(self, index):
        return self.metadata[index]

    def getStar(self, index):
        return self.stars[index]

    def getStars(self):
        return self.stars

    def getMetadata(self):
        return self.metadata


class Filter(object):
    def __init__(self, producer=None, query=None):
        self.producer = producer
        self.type = "filter"
        self.query = query
        self.distM = query.getDistanceMatrix()
        self.anchorElement = self.query.getAnchor().getId()
        self.margin = query.getMargin()

    def getNext(self):

        listTuple = self.producer.getNext()

        if listTuple == "end":
            return listTuple
        elif not listTuple:
            return listTuple
        else:
            listResult = []
            epsilon = self.query.getEpsilon() * self.query.getMaxDistance()
            for t in listTuple:
                result = self.checkScale(t, self.margin, epsilon)
                if result:
                    listResult.append(t)

        if len(listResult) == 0:
            return "end"
        else:
            return listResult

    def checkScale(self, candidatesolution, margin=0, epsilon=0):
        self.starsTuple = candidatesolution.getStars()
        self.metadataTuple = candidatesolution.getMetadata()
        self.margin = margin

        k = 0
        for i in range(len(self.starsTuple)):
            rai = self.starsTuple[i].getRa()
            deci = self.starsTuple[i].getDec()
            if i == 0:
                reli = self.anchorElement
            else:
                reli = self.metadataTuple[i]
            for j in range(i + 1, len(self.starsTuple)):
                raj = self.starsTuple[j].getRa()
                decj = self.starsTuple[j].getDec()
                relj = self.metadataTuple[j]
                dist = EucDist(rai, raj, deci, decj)
                if k == 0:
                    k = dist / self.distM[reli][relj]
                else:
                    ratio = dist / self.distM[reli][relj]
                    if not (round(ratio) <= round(k) + epsilon):
                        if not (round(ratio) >= round(k) - epsilon):
                            return False
        return True


class Join(object):
    def __init__(self, rightRelation, leftJoin=None, leftRelation=None, query=None):
        self.rightR = rightRelation
        self.idR = self.rightR.getRelationId()
        self.type = "join"
        self.leftJ = leftJoin
        self.leftRelation = leftRelation
        self.query = query
        self.distM = query.getDistanceMatrix()
        if self.leftJ is None:
            self.stars = self.leftRelation.getStars()
            self.starIndex = 0
            self.sizeLeftleave = len(self.stars)

    def getNext(self):
        epsilon = self.query.getEpsilon() * self.query.getMaxDistance()
        listTuple = []
        newListTuple = []
        if self.leftRelation is None:
            listTuple = self.leftJ.getNext()
            if listTuple == False:
                return listTuple
            elif listTuple == "end":
                return listTuple
        else:
            if self.starIndex == self.sizeLeftleave:
                listTuple = "end"
                return listTuple
            else:
                listTuple.append(self.stars[self.starIndex])
                self.starIndex += 1

        for l in range(len(listTuple)):
            genTuple = listTuple[l]
            tuple = Tuple()
            if self.leftJ is None:
                tuple.addStar(genTuple[0], self.leftRelation.getRelationId())
                tuple.addStar(genTuple[1], self.leftRelation.getRelationId())
            else:
                tuple.addTuple(genTuple)
            anchor = tuple.getStar(0)
            idAnchor = anchor.getId()
            distM = self.query.getDistanceMatrix()

            for t in self.rightR.getStars():
                match = True
                rightId = t[0].getId()
                if idAnchor == rightId:
                    for i in range(len(tuple.getStars()) - 1):  # Checks pairwise distances with all elements in tuple
                        dist = EucDist(tuple.getStar(i + 1).getRa(), t[1].getRa(), tuple.getStar(i + 1).getDec(),
                                       t[1].getDec())
                        distanceMatrix = distM[self.rightR.getRelationId()][tuple.getMetadataPos(i + 1)]
                        if (distanceMatrix - epsilon) <= dist <= (distanceMatrix + epsilon):
                            s = tuple.getStar(i + 1)
                            if s.getId() == t[1].getId():
                                match = False
                        else:
                            match = False
                            break

                    if match:
                        newTuple = Tuple()
                        newTuple.addTuple(tuple)
                        newTuple.addStar(t[1], self.rightR.getRelationId())
                        newListTuple.append(newTuple)

        return newListTuple


class Plan(object):
    def __init__(self, query=None):
        self.query = query

    def buildPlan(self, relations, filter_operation=False):
        joinOld = None
        # root = None
        # join = None

        for i in range(len(relations.getRelations()) - 1):
            if i == 0:
                join = Join(relations.getRelations()[i + 1], None, relations.getRelations()[i], self.query)
            else:
                join = Join(relations.getRelations()[i + 1], joinOld, None, self.query)
            joinOld = join
        if filter_operation:
            root = Filter(joinOld, self.query)
        else:
            root = joinOld

        return root


class Relation(object):
    def __init__(self, query_id=0, stars=[]):
        self.query_id = query_id
        self.stars = stars

    def addStar(self, key, element):
        self.stars.append([key, element])

    def getStars(self):
        return self.stars

    def getRelationId(self):
        return self.query_id


class Relations(object):
    def __init__(self):
        self.relations = []

    def addRelation(self, relation):
        self.relations.append(relation)

    def getRelations(self):
        return self.relations

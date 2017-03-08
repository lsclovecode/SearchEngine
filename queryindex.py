import math


# d is a dictionary
def parseQuery(q):
    q = q.strip()
    return q.spilt(" ")


def getDocsHaveThisWord(term):  # given a single term, return all docs that contains this term
    return [int(x.keys()[0]) for x in d[term]['docs']]  # d[term]['doc'] returns a list of dictionaries


def intersectLists(lists):  # given a list of each term's list, find the list which contains all the terms
    if len(lists) == 0:
        return []
    # start intersecting from the smaller list
    lists.sort(key=len)
    return list(reduce(lambda x, y: set(x) & set(y), lists))


def getPosition(term, docid):
    posLists = []
    for eachdoc in d[term]['docs']:
        if eachdoc.has_key(docid):
            posLists.append(eachdoc[docid]['p'])
    return posLists


# give a query, first parse it into term list, for each term find the docs that contains the term,
# then use the intersect function to find the docs that contains all the words;

def checkNGramPosition(posLists):  # given a sequence of each term's position list
    for i in xrange(len(posLists)):
        posLists[i] = [x - i for x in posLists[i]]
    result = intersectLists(posLists)
    return result


def textQueryDocs(termList):
    for term in termList:
        lists.append(getDocsHaveThisWord(term))
    docList = intersectLists(lists)
    return docList


def phaseQueryDocs(termList):  # given a list of terms
    # lists = []
    for term in termList:
        lists.append(getDocsHaveThisWord(term))
    docList = intersectLists(lists)  # returns a list that contains all the terms
    finalList = []
    for docid in docList:
        temp = []
        for term in termList:
            temp.append(getPosition(term, docid))
        result = checkNGramPosition(temp)
        if len(result) != 0:
            finalList.append(docid)
    return finalList
# vector1, vector2 are two lists with same length
# length is the length of a doc vector

# dic1 of query tf-idf
# dic2 of document tf-idf
def getQueryVector(termList):
    queryvector = []
    querylength = 0
    for term in termList:
        queryvector.append(dic1[term])
        querylength = querylength + dic1[term] * dic1[term]
    querylength = math.sqrt(querylength)
    for i in range(len(queryvector)):
        queryvector[i] = queryvector[i] / querylength

def computeCosineSimilarity(queryvector, docvector, doclength):
    vectorsum = 0
    for i in range(len(queryvector)):
        vectorsum = queryvector[i] * docvector[i] + vectorsum
    return vectorsum / math.sqrt(doclength)


# docList is a list of docids, you should calculate the similarity of the qvecor of each docid's vector
# then rank, return a ranked list
def rankDocuments(docList, termList):
    scoredic = {}
    queryvector = getQueryVector(termList)
    for docid in docList:
        doclength, docvector = dic2[docid][termList]
        score = computeCosineSimilarity(queryvector, docvector, doclength)
        scoredic[score] = docid
    sortedscore = sorted(scoredic.keys(), cmp=None, key=None, reverse=False)
    rank = []
    for i in sortedscore:
        rank.append(scoredic[i])
    return rank






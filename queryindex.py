import math


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


def getTfidfValue(term, docid):
    tf = 0
    df = 0
    df = d[term]['df']
    for eachdoc in d[term]['docs']:
        if eachdoc.has_key(docid):
            tf = eachdoc[docid]['tf']
    return (1 + math.log(tf)) * (math.log(500.0 / df))


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

def rankDocuments(docList):

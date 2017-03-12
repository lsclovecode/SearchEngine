from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize
import re
import math
import numpy as np
import time
from nltk.stem import SnowballStemmer
stemmer = SnowballStemmer("english")
from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.test_database
index = db.tdIndex
length = db.docInfo
idurl = db.urlIndex
titleindex = db.titleIndex



def tokenize(text):
    try:
        text_tokenized = word_tokenize(text)
    except:
        text = unicode(text, errors='ignore')
        text_tokenized = word_tokenize(text)
    return text_tokenized


def parseWordList(tokens):
    tokenlist = []
    for token in tokens:
        try:
            token = token.translate(string.punctuation)
        except:
            token = token
        m = re.match(r'^[a-zA-Z]+$', token)
        if m:
            #if not token in stopwords.words('english'):
            tokenlist.append(token.encode('utf-8'))
    return tokenlist


def parseQuery(q):
    q = q.strip()
    termlist = q.split(" ")
    termlist = [stemmer.stem(term).encode('utf-8') for term in termlist]
    return termlist

def getDocsHaveThisWord(term):  # given a single term, return all docs that contains this term

    d = index.find_one({"_id": term})
    return [int(x) for x in d['docid'].keys()]  # d[term]['doc'] returns a list of dictionaries


def intersectLists(lists):  # given a list of each term's list, find the list which contains all the terms
    if len(lists) == 0:
        return []
    # start intersecting from the smaller list
    lists.sort(key=len)
    result = list(reduce(lambda x, y: set(x) & set(y), lists))
    return sorted(result)


def getPosition(term, docid):
    d = index.find_one({"_id": term})
    return d['docid'][str(docid)]['p']


# give a query, first parse it into term list, for each term find the docs that contains the term,
# then use the intersect function to find the docs that contains all the words;

def checkNGramPosition(posLists):  # given a sequence of each term's position list
    for i in xrange(len(posLists)):
        posLists[i] = [x - i for x in posLists[i]]
    result = intersectLists(posLists)
    return result


def textQueryDocs(termList):
    lists = []
    for term in termList:
        lists.append(getDocsHaveThisWord(term))
    docList = intersectLists(lists)
    return docList


def phaseQueryDocs1Param(termList):  # given a list of terms
    lists = []
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

def phaseQueryDocs2Param(termList, docList):  # given a list of terms
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
'''The query may contain repetitive words'''
def getQueryVector(termList):
    queryvector = []
    querylength = 0
    for term in termList:
        df = index.find_one({"_id": term})['df']
        df = math.log(37438.0 / df)
        queryvector.append(df)
        querylength += df * df
    querylength = math.sqrt(querylength)
    for i in range(len(queryvector)):
        queryvector[i] = queryvector[i] / querylength
    return queryvector

def getDocVector(termList, docid):
    docVector = []
    try:
        docLength = length.find_one({"_id": docid})['length']
    except:
        docLength = 5000
    for term in termList:
        d = index.find_one({"_id": term})
        tfidf = d['docid'][str(docid)]['tfidf'] / docLength
        docVector.append(tfidf)
    return docVector


def computeCosineSimilarity(queryvector, docvector):
    q = np.array(queryvector)
    d = np.array(docvector)
    resultlist = (q * d).tolist()
    return sum(resultlist)

def checkATermInTitle(term, docid):
    d = index.find_one({"_id": term})
    return d['docid'][str(docid)]['t'] == 1

def checkTermListInTitle(termList, docid):
    for term in termList:
        if not checkATermInTitle(term, docid):
            return False
    return True

def findDocsInTitle(termList, docList):
    result = []
    for doc in docList:
        if checkTermListInTitle(termList, doc):
            result.append(doc)
    return result

def findDocsInTitleByTitleIndex(termList):
    lists = []
    for term in termList:
        d = titleindex.find_one({"_id": term})
        lists.append([int(x) for x in d['docid'].keys()])
    docList = intersectLists(lists)

    finalList = []
    for docid in docList:
        temp = []
        for term in termList:
            d = titleindex.find_one({"_id": term})
            temp.append(d['docid'][str(docid)])
        result = checkNGramPosition(temp)
        if len(result) != 0:
            finalList.append(docid)
    return finalList

# docList is a list of docids, you should calculate the similarity of the qvecor of each docid's vector
# then rank, return a ranked list
def rankDocuments(docList, termList, queryvector):
    scoredic = {}
    #print queryvector

    for docid in docList:
        docvector = getDocVector(termList, docid)
        #print docvector
        score = computeCosineSimilarity(queryvector, docvector)
        #print "score", score
        scoredic[score] = docid

    sortedscore = sorted(scoredic.keys(), cmp=None, key=None, reverse=True)
    #print sortedscore
    rank = []
    for i in sortedscore:
        rank.append(scoredic[i])
    return rank




def search(input):
    termList = parseQuery(input)
    #print termList
    queryvector = getQueryVector(termList)
    #print queryvector
    docList = textQueryDocs(termList)
    #print docList
    #docsInTitle = findDocsInTitle(termList, docList)
    docsInTitle = findDocsInTitleByTitleIndex(termList)
    #print len(docsInTitle)
    #print docsInTitle
    result = []
    if len(docsInTitle) >= 5:
        result = rankDocuments(docsInTitle, termList, queryvector)
        return result[:5]
    else:
        remaining = list(set(docList) - set(docsInTitle))
        remainingWithPositionChecked = phaseQueryDocs2Param(termList, remaining)
        result1 = rankDocuments(docsInTitle, termList, queryvector)
        if len(remainingWithPositionChecked) != 0:
            result2 = rankDocuments(remainingWithPositionChecked, termList, queryvector)
        else:
            result2 = rankDocuments(remaining, termList, queryvector)
        result = result1 + result2
        if len(result) >= 5:
            return result[:5]
    return result
#words = ["mondego", "software engineering", "security", "student affairs", "graduate courses", "crista lopes", "REST", "computer games", "information retrieval", "machine learning"]


word = raw_input()
t1 = time.clock()
result = search(word)
t2 = time.clock()
print t2 - t1, "seconds"
print result

term = parseQuery(word)[0]

for id in result:
    i = id / 500
    j = id % 500
    pos = getPosition(term, id)[0]
    with open(str(i) + '/' + str(j)) as f:
        soup = BeautifulSoup(f, 'lxml')
    try:
        body = soup.body.text
    except:
        print ""
    for script in soup(["script", "style"]):
        script.decompose()
    fulltext = soup.get_text().encode('utf-8')
    fulltext_tokenized = tokenize(fulltext)
    fulltext_list = parseWordList(fulltext_tokenized)
    if pos < 3:
        demo = fulltext_list[pos: pos + 5]
    else:
        demo = fulltext_list[pos - 2: pos + 5]
    s = ''
    for word in demo:
        s += ' ' + word
    urlname = idurl.find_one({"id": id})['url']
    if "ics" in urlname:
        print "http://" + urlname
        print s


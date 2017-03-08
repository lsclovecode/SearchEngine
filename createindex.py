from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from collections import defaultdict
stemmer = SnowballStemmer("english")
import re
import sys
import string
import json
import math
from pymongo import MongoClient
reload(sys)
#####
sys.setdefaultencoding('utf-8')

index = defaultdict(list)
numberOfDocuments = 0


client = MongoClient('localhost', 27017)
db = client.test_database
collection = db.tdIndex


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
            if not token in stopwords.words('english'):
                tokenlist.append(stemmer.stem(token).encode('utf-8'))
    return tokenlist


for i in range(1):
    for j in range(3):
        docid = 500 * i + j
        try:
            soup = BeautifulSoup(open(str(i) + '/' + str(j)), 'lxml')
            try:
                body = soup.body.text
            except:
                print 'folder', i, 'doc', j, "is not a valid html"
                continue
            for script in soup(["script", "style"]):
                script.decompose()
            fulltext = soup.get_text().encode('utf-8')
            fulltext_tokenized = tokenize(fulltext)
            fulltext_list = parseWordList(fulltext_tokenized)
            numberOfDocuments += 1

            try:
                title = soup.title.text
                titlelist = parseWordList(tokenize(title))
            except:
                print 'folder', i, 'doc', j, "does not have a title"
                titlelist = []
            termdict = {}

            for position, term in enumerate(fulltext_list):
                try:
                    termdict[term][1][1].append(position)
                except:
                    if term in titlelist:
                        termdict[term] = [docid, [[1], [position]]]
                    else:
                        termdict[term] = [docid, [[0], [position]]]
            for term, postingpage in termdict.iteritems():
                index[term].append(postingpage)
        except:
            print 'folder', i, 'doc', j, "It's a not valid html"
            continue




'''{'_word_':{'df':3, 'docs':['_docid_':{'tf':5, 't': 0/1, 'pos':[5,7]}} ]     }'''
docIndex = {} #doc normalize length

for term, doc in index.iteritems():
    finalindex = {}
    df = len(doc)
    finalindex["_id"] = term
    finalindex['df'] = df
    finalindex['docs'] = []
    for eachdoc in doc:
        eachdocsummary = {}
        docid = eachdoc[0]
        eachdocsummary["docid"] = docid
        tf = 0
        if eachdoc[1][0][0] == 1:
            tf = 20 + len(eachdoc[1][1])
            eachdocsummary['t'] = 1
        elif eachdoc[1][0][0] == 0:
            tf = len(eachdoc[1][1])
            eachdocsummary['t'] = 0
        eachdocsummary['tf'] = tf
        eachdocsummary['p'] = eachdoc[1][1]
        tfidf = (1 + math.log(tf)) * (math.log(500.0 / df))
        eachdocsummary['tfidf'] = tfidf
        if docid in docIndex:
            docIndex[docid] += tfidf * tfidf
        else:
            docIndex[docid] = tfidf * tfidf
        finalindex['docs'].append(eachdocsummary)
    collection.insert_one(finalindex)

doccollection = db.docInfo
for docid in docIndex:
    record = {}
    record['_id'] = docid
    record['length'] = math.sqrt(docIndex[docid])
    doccollection.insert_one(record)

'''
print 'docindex /n', docIndex


print 'total valid documents', numberOfDocuments
 
 
with open('test.json', 'w') as ff:
   json.dump(finalindex, ff, indent=2)


'''

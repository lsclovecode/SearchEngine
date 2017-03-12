from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from collections import defaultdict

stemmer = SnowballStemmer("english")
import re
import sys
import string
import math
from pymongo import MongoClient

reload(sys)
sys.setdefaultencoding('utf-8')

index = defaultdict(list)
numberOfDocuments = 0

client = MongoClient('localhost', 27017)
db = client.test_database
collection = db.titleIndex


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
            tokenlist.append(stemmer.stem(token).encode('utf-8'))
    return tokenlist


for i in range(75):
    for j in range(500):
        docid = 500 * i + j
        try:
            with open(str(i) + '/' + str(j)) as f:
                soup = BeautifulSoup(f, 'lxml')
            try:
                body = soup.body.text
            except:
                print 'folder', i, 'doc', j, "is not a valid html"
                continue
            try:
                title = soup.title.text
                titlelist = parseWordList(tokenize(title))
            except:
                print 'folder', i, 'doc', j, "does not have a title"
                continue
                titlelist = []
            termdict = {}

            for position, term in enumerate(titlelist):
                if not term in stopwords.words('english'):
                    try:
                        termdict[term][1][1].append(position)
                    except:
                        termdict[term] = [docid, [[1], [position]]]
            for term, postingpage in termdict.iteritems():
                index[term].append(postingpage)
        except:
            print 'folder', i, 'doc', j, "It's a not valid html"
            continue

for term, doc in index.iteritems():
    finalindex = {}
    df = len(doc)
    finalindex["_id"] = term
    finalindex["docid"] = {}
    for eachdoc in doc:
        docid = eachdoc[0]
        finalindex["docid"][str(docid)] = eachdoc[1][1]
    collection.insert_one(finalindex)


print "finished"

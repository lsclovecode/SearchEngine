# SearchEngine

* first turn on you mongod in your terminal

* run createindex.py and run createindexForTitle.py tp store data in you local database; be careful to add 497 498 499 , three empty files in folder 74

*run docidDB.py , don't forget to use bookkeeping.json to create id, url key value pairs

* run queryindex.py, type the words you want to search in terminal



#Combine with PageRank
To improve the search result, we consider both tf-idf score and pagerank score by calculating the harmonic mean of them.
In mathematics, the harmonic mean (sometimes called the subcontrary mean) is one of several kinds of average, and in particular one of the Pythagorean means. Compare to arithmetic mean (AM) and the geometric mean (GM). Harmonic mean(HM) generates the smallest result. It lean strongly towards the least elements of the list. So in our experiment, either low score of tf-idf or pagerank would lead to a low score. This prevents some particular high score of tf-idf because of short and precise title, or solely high pagerank score because of circular self reference.
We made some improvement on several terms such as "graduate courses", "computer games". But for some other term such as "security" and "information retrieval", there weren't any improvement since those top rank results of tf-idf has high pagerank scores too because of the circular reference.

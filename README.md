**Search engine for “ics.uci.edu” in python**

Developed a complete search engine for “ics.uci.edu” domain which takes in the user query and returns the top-hits based on the ranking algorithm. The results are evaluated using NDCG@5 taking google as the oracle (ground truth). 

**Description**

Crawled the “ics.uci.edu” domain and stored the web pages. The web pages were crawled based on their URLs. If a URL was not valid, it was filtered out. 

Constructed an index on the pages stored by crawling the “ics.uci.edu” domain. The index was based on:-
Terms/words along with their term frequency, number of documents it is present in, document-id of documents it is present in along with their positions.
Terms/words along with their tf-idf weights. Updated tf-idf scores by adding weights based on tags and words in URL.

Computed the cosine scores for various document-query pairs and sorted the results in descending order to get top hits.

Whenever a user types in a query, the pages corresponding to that are presented with the highest ranked pages(ones with highest cosine scores) at the top. 

The clickable URLs of the top hits are presented along with text snippets. 

The results are optimized to a large extent and compared with the Google oracle using NDCG@5 evaluation metric. The results of the search engine were good enough to ease search for the users.


**Authors**

Shruti Khurana <skhuran1@uci.edu><br />
Reeta Singh

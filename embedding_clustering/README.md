# embedding_clustering

## main
the whole process, containing all the sub-process, like data-construction, clustering and so forth~\
\
the main process of answer qualification examination contains:
1. data construction, get qa_list
2. sentence embedding, get the matrix of sentences
3. compute similarity between given questions provided in the standard document and the questions we found in the conversation
4. score the answers with gpt

besides, we've also done some work on finding `standard questionS aka highly frequent questions`:
1. sentence embedding
2. clustering
3. summarize on the different clustering
4. TODO: HOW TO ANSWER THE QUESTIONS?


## data construction

analyze raw data and construct `Q&A list`

## se_ward
use `shibing624/text2vec-base-chinese` to calculate sentence embeddings\
cluster the sentence embeddings with the algorithm `Ward Hierarchical`

## gan_bertopic
use the sentence embeddings from `GanymedeNil/text2vec-large-chinese`\
add the sentence embeddings to the topic model `BERTopic`

## questions_match
use `shibing624/text2vec-base-chinese` to calculate sentence embeddings\
match the sentence embeddings with cosine similarity or any other methods? (*to be confirmed*)

## gpt_score
use OPAI_API to score the answers of customers service

## data
raw data and some intermediate data, like qa_list and so forth~

## clustered data
data of clusters, and the summary results
# wordnet_words_clustering
This project offers a very simple and efficient and useful tool for the analysis of set of english words and the topic covered by them.  
Given a list of words, the algorithm proposed gather the set of Wordnet's hypernyms for each of them.  
A new cluster is created for each synset found, and all the words listing it in their hypernyms set are added to it.  
This is an overlapping clustering and considering all the possible meaning that a word could present, it tries to associate it to a more general concept.  

 ## Usage
This project has been developed using version 3.6 of Python and uses the nltk library.
A simple guide for using it can be retrieved by executing:
```console
user@machine:$ python3 wordnet_clustering.py --help
```
To easily analyze the topics covered by the words in the input set, different parameters values should be used and tuned.  
The available parameters are:
* Minimum hypernym depth: minimum allowed depth for an hypernym in the Wordnet synsets tree, in order to make it eligible to be a cluster id.
It is useful to filter out all those concept that have a too general meaning and with low informativeness.
* Minimum cluster size: minimum size allowed for a cluster, useful for filtering out clusters representing too particular concepts.
* Maximum cluster size: maximum size allowed for a cluster, useful for filtering out clusters that have a too general meaning, because populated by too many words.

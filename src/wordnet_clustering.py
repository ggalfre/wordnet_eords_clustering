import nltk
from nltk.corpus import wordnet as wn
import argparse
import sys
import copy


def get_words(file_path):
    """
    This function read the words from the file specified in file_path.
    Words must be separated by a newline character '\n' or white space in general.

    :param file_path:   path of the text file storing the words to be clustered.
    :return: words:     set of the words read from file
    """

    words = set()
    count = 0

    try:
        with open(file_path, 'r', encoding='utf8') as file:
            for counter, line in enumerate(file):
                for word in line.split():
                    words.add(word)
                    count += 1
    except Exception as e:
        print(str(e))
        exit(1)

    print('Total number of words: ' + str(len(words)) + '.')
    if count != len(words):
        print('Warning: some of the words in the file are repeated.')

    return words


def store_words(file_path, words_set):
    """
    This function store the set of words in a file.

    :param file_path:   file where to store the words.
    :param words_set:   set containing the words to be stored in file
    """

    with open(file_path, 'w', encoding='utf8') as file:
        for word in words_set:
            file.write(word + '\n')



def get_clusters(words_set, min_depth=0):
    """
    This function generates the clusters of words following a simple strategy.
    For each word from the initial pool the set of synsets associated to the word itself and to all its hypernyms
    is generated. The synsets at invalid depth are fultered out, and the remaining are used as identifiers for the
    clusters to which the word belongs.
    Accordingly, an arbitrary word will probably belong to multiple clusters, but with different levels of concept
    generality.
    The minimum depth requirement is used to filter out the synsets very low informativeness.

    :param words_set:   set of words to be clustered.
    :param min_depth:   minimum depth allow for an hypernym to be eligible as a cluster label
    :return clusters:   dictionary having as keys strings identifying the clusters and generated as the Wordnet words
                        composing the corresponding synsets. The values are sets of words, retrieved from the words_set
                        parameter, members of the clusters.
    :return words_to_clusters:  dictionary having as keys the words from the words_set parameter and as values the set
                                clusters' ids in which they are inserted.
    :return not_inserted:   set of words from the words_set parameter that haven't been clustered because all the
                            synsets found in their hypernyms closure have invelid depths
    :return not_found:  set of words from the words_set parameter that haven't been recognized in the Wordnet collection
    """

    clusters = dict()
    words_to_clusters = dict()
    not_inserted = set()
    not_found = set()

    # lambda function used for the Wordnet clsure method
    hyp = lambda s:s.hypernyms()

    for word in words_set:

        found = False
        hypers_set = set()

        # for each meaning of the word (synset)
        for synset in wn.synsets(word):

            found = True

            # the synset itself is also considered for the clustering purpose
            # check if the depth is valid
            if synset.min_depth() >= min_depth:
                # adding the synset to the list
                hypers_set.add(synset)

            # for each hypernym related to that meaning
            for hypernym in synset.closure(hyp):
                # check if the depth is valid
                if hypernym.min_depth() >= min_depth:
                    # adding the synset to the list
                    hypers_set.add(hypernym)

        # checking if valid synsets are found and if valid
        if found:
            if len(hypers_set) <= 0:
                # inserting the word in the set of strings recognized as Wordnet words, but with no valid depth in their
                # hypernyms closure set
                not_inserted.add(word)
            else:
                # convertung synset id in a string showing the words by which its concept is identified
                words_to_clusters[word] = set()
                for x in hypers_set:
                    key = x.name()
                    # inserting word in the clusters found
                    if key not in clusters:
                        clusters[key] = set()
                    if word not in clusters[key]:
                        clusters[key].add(word)
                    # associating the clusters found to the word
                        words_to_clusters[word].add(key)
        else:
            # inserting the word in the set of stirngs not belonging to the Wordnet collection
            not_found.add(word)

    return clusters, words_to_clusters, not_inserted, not_found



def filter_by_size(clusters, words_to_clusters=None, max_size=sys.maxsize, min_size=0):
    """
    This function simply filter out the clusters with a size not fitting in the [min_size, max_size] range.
    The maximum size requirement is useful to filter out those cluster associated to concept that appear deep enough
    in the Wordnet synset collection, but that reprent anyways very low informativeness.

    :param clusters:    dictionary having as keys strings identifying the clusters and generated as the Wordnet words
                        composing the corresponding synsets. The values are sets of words, retrieved from the words_set
                        parameter, members of the clusters.
    :param words_to_clusters:   dictionary having as keys the words from the words_set parameter and as values the set
                                clusters' ids in which they are inserted.
    :param max_size:    maximum allowed size for clusters
    :param min_size:    minimum allowed size for clusters
    :return new_clusters:   copy of the clusters received as parameter, filtered by the size constraint
    :return new_words_to_clusters: copy of the words to clusters parameter, updated accordingly to filtering operations
    :return removed: set of words removed completely from the clustering due to clusters' sizes requirements
    """

    new_clusters = dict()
    new_words_to_clusters = copy.deepcopy(words_to_clusters)
    removed = set()

    # for each cluster
    for element in clusters.items():
        # size is compared with threshold
        if len(element[1]) > max_size or len(element[1]) < min_size:

            # for each word in the cluster
            for word in element[1]:

                if new_words_to_clusters is not None:
                    # updating the words to clusters structure accordingly
                    if word in new_words_to_clusters:
                        if element[0] in new_words_to_clusters[word]:
                            new_words_to_clusters[word].discard(element[0])
                        if len(new_words_to_clusters[word]) <= 0:
                            del new_words_to_clusters[word]
                            removed.add(word)
                    else:
                        print('Warning: Inconsistency has been found between clusters '
                              'and the words to clusters structures.')
        else:
            new_clusters[element[0]] = element[1]

    return new_clusters, new_words_to_clusters, removed



def get_counter_from_dict(collection):
    """
    This function given a dictionary having set of strings as values, return the corresponding list of tuples having the keys as first
    element and the dimension of the associated collection as second one

    :param collection: dictionary having collections of strings as values.
    :return result: list of tuples.
    """

    result = list()
    for x in collection.items():
        result.append((x[0], len(x[1])))
    return result


def store_clusters_ranking(file_path, clusters):
    """
    this function simply stores in the file selected the ranking of clusters ordered by decreasing number of elements.

    :param file_path: path of the file where to store the information.

    """

    with open(file_path, 'w', encoding='utf8') as sorted_file:
        elements_counter = get_counter_from_dict(clusters)
        counter = 0
        for element in sorted(elements_counter, key=lambda kv: kv[1], reverse=True):
            counter += 1
            sorted_file.write(str(counter) + ')  ' + element[0] + ': ' + str(element[1]) + ' elements\n\t' +
                              str(clusters[element[0]]) + '\n\n')


def get_listed(clusters):
    """
    This function convert the clusters structure in a more readable way. It simply substitute the synsets names used as
    keys of the dictionary into a string consisting in the synsets depths and the words belonging to them,separated
    by commas.

    :param clusters:    clusters retrieved.
    :return readable_clusters:  informative version of the input dictionary.
    """

    readable_clusters = dict()

    for element in clusters.items():

        # all synsets lemmas are used as key
        lemmas = list(wn.synset(element[0]).lemma_names())
        lemmas.sort()
        # constructing the key string
        key = '[synset depth = ' + str(wn.synset(element[0]).min_depth()) + '] '
        key += ', '.join(iter(lemmas))
        readable_clusters[key] = element[1]

    return readable_clusters


parser = argparse.ArgumentParser(description='Applies Wordnet based algorithm to group words from the file selected '
                                             'into meaningful clusters related to hypernyms synsets.')
parser.add_argument(dest='words_path',
                    action='store',
                    nargs=1,
                    type=str,
                    help='Path of the file storing the dataset to be analyzed.'
                    )
parser.add_argument(dest='results_path',
                    action='store',
                    nargs=1,
                    type=str,
                    help='Path of the file where to store results.'
                    )
parser.add_argument('-d', '--min_allowed_depth',
                    dest='min_allowed_depth',
                    action='store',
                    nargs=1,
                    type=int,
                    help='Lowest value allowed for the depth of an hypernym used as a cluster.'
                    )
parser.add_argument('-x', '--max_cluster_size',
                    dest='max_cluster_size',
                    action='store',
                    nargs=1,
                    type=int,
                    help='Optional argument to specify the maximum allowed size for a cluster.'
                    )
parser.add_argument('-m', '--min_cluster_size',
                    dest='min_cluster_size',
                    action='store',
                    nargs=1,
                    type=int,
                    help='Optional argument to specify the minimum allowed size for a cluster.'
                    )


# parsing arguments
args = parser.parse_args()

words_path = args.words_path[0]
result_path = args.results_path[0]
min_depth = 0
if args.min_allowed_depth is not None:
    min_depth = args.min_allowed_depth[0]
max_size = sys.maxsize
if args.max_cluster_size is not None:
    max_size = args.max_cluster_size[0]
min_size = 0
if args.min_cluster_size is not None:
    max_size = args.min_cluster_size[0]

# downloading wordnet
nltk.download('wordnet')
nltk.download('omw')

# reading list of words
words = get_words(words_path)

# clustering
print("\nGenerating clusters...")
clusters, words_to_clusters, excluded_by_depth, not_found = get_clusters(words, min_depth)

# filtering the clusters with invalid size
clusters, words_to_clusters, excluded_by_size = filter_by_size(clusters, words_to_clusters, max_size, min_size)

# printing resulting info
print("\n\nNumber of words: "+ str(len(words)))
print("Number of clusters: "+str(len(clusters)))
print("\nNumber of words fltered by hypernyms/synsets depth: " + str(len(excluded_by_depth)))
print("Number of words fltered by clusters' sizes: " + str(len(excluded_by_size)))
print("Number of words not recognized as Wordnet collection's element: " + str(len(not_found)))

# converting keys in listed form
clusters = get_listed(clusters)

# storing clusters ranking in files
# file name is created including the values of the parameteres used
# firstly the file extension if present is removed
dot_index = result_path.rfind(".")
if dot_index != -1:
    result_path = result_path[:dot_index]
file_descr = '_mindepth' + str(min_depth)
if args.max_cluster_size is not None:
    file_descr += "_maxsz" + str(max_size)
if args.min_cluster_size is not None:
    file_descr += "_minsz" + str(min_size)
result_path += file_descr + '.txt'

# storing lis of excluded words in file
store_words('words_excluded_by_depth' + file_descr + '.txt', excluded_by_depth)
store_words('words_excluded_by_size' + file_descr + '.txt', excluded_by_size)
store_words('words_not_found' + file_descr + '.txt', not_found)

# storing clusters in txt file
store_clusters_ranking(result_path, clusters)

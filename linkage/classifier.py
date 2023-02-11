import pathlib
from .datatypes import MATCH, NON_MATCH, MAYBE_MATCH, SimilarityTuple
from pprint import pprint
import csv
from .clean import clean_opensecrets_data, clean_ppp_data
from .similarity import calculate_similarity_tuple

# expected_strict_classifier = {
#     ("high", "medium", True): MATCH,
#     ("high", "high", True): MATCH,
#     ("high", "low", False): MAYBE_MATCH,
#     ("high", "high", False): MAYBE_MATCH,
#     ("high", "high", True): MATCH,
#     ("medium", "medium", False): NON_MATCH,
#     ("low", "high", True): NON_MATCH,
#     ("low", "low", False): NON_MATCH,
#     ("medium", "high", False): MAYBE_MATCH,
#     ("medium", "low", False): NON_MATCH,
#     ("medium", "high", True): MAYBE_MATCH,
# }
matches_filename = pathlib.Path(__file__).parent / "data/matches.csv"
non_matches_filename = pathlib.Path(__file__).parent / "data/non_matches.csv"

def sort_similarities(sim_list):
    """
    This function takes a list of tuples containing SimilarityTuples and their
    corresponding likelihoods and sorts the list from highest to lowest likelihood
    of representing a match.
    Inputs:
        `sim_list` should be a list of tuples where each tuple contains a
        SimilarityTuple and two floats representing the likelihood of the tuple
        representing a match and the likelihood of the tuple representing a
        non-match.
    Returns:
        Sorted list of tuples in the same format as the input list.
    Example:
    [
        (SimilarityTuple("high", "high" True), 0.8, 0.1),
        (SimilarityTuple("high", "medium" True), 0.9, 0.2),
        ... # more rows
    ]
    """
    if len(sim_list) != 18:
        raise ValueError("sim_list must have 18 elements")
    if len(sim_list[0]) != 3:
        raise ValueError("sim_list must have 3 elements per tuple")

    def sort_key(sim_tuple):
        if sim_tuple[2] == 0:
            return sim_tuple[1] * 100000000  
        return sim_tuple[1] / sim_tuple[2]

    return sorted(sim_list, key=sort_key, reverse=True)


def read_file(filename):
    return csv.DictReader(open(filename))


def train_classifier(max_false_positives, max_false_negatives):
    """
    Train a classifier using the training data and the given
    maximum false positives and false negatives.
    Inputs:
        max_false_positives (float): The maximum rate of false positives
            the classifier is allowed to have.
        max_false_negatives (float): The maximum rate of false negatives
            the classifier is allowed to have.
    Returns:
        A dictionary mapping similarity tuples to match types.
        There must be one entry for each possible similarity tuple.
    """
    

    # TODO: Implement this function
    dfm = None
    dfn = None
    matches = {}
    mlen = 0
    nmatches = {}
    nlen = 0
    dfop = clean_opensecrets_data() # list of tuples
    dfppp = clean_ppp_data() # list of tuples

    # change list of tuples to dict to improve the efficiency
    # use id as the key and tuple as the value
    dfop = { i.id:i for i in dfop}
    dfppp = { i.id:i for i in dfppp}

    dfm = read_file(matches_filename)
    for i in dfm:
        tup1 = None
        tup2 = None
        # instead of searching linearly, use id to get access to the right row in another csv
        tup1 = dfop[int(i['os_id'])]
        tup2 = dfppp[int(i['ppp_id'])]
        result = calculate_similarity_tuple(tup1, tup2)
        # if already in the dic, just add 1
        if result in matches.keys(): 
            matches[result] = matches[result] + 1
            mlen = mlen + 1
        # if not assign 1
        else: 
            matches[result] = 1
            mlen = mlen + 1
    
    dfn = read_file(non_matches_filename)
    for i in dfn:
        tup1 = None
        tup2 = None
        tup1 = dfop[int(i['os_id'])]
        tup2 = dfppp[int(i['ppp_id'])]
        result = calculate_similarity_tuple(tup1, tup2)
        if result in nmatches.keys():
            nmatches[result] = nmatches[result] + 1
            nlen = nlen + 1
        else:
            nmatches[result] = 1
            nlen = nlen + 1   

    # get all types found in the csv, types means tuples look like ('high','low',True)
    kinds = set(list(matches.keys())+list(nmatches.keys()))
    ans = []
    # add types not found in the csv
    for i in ['high','medium','low']: 
        for j in ['high','medium','low']:
            for k in [True, False]:
                temp = SimilarityTuple(i,j,k) 
                if temp not in kinds:
                    ans.extend([(temp,0,0)])
                else:
                    temp2 = [temp,0,0]
                    if temp in matches.keys():
                        temp2[1] = matches[temp]/mlen
                    if temp in nmatches.keys():
                        temp2[2] = nmatches[temp]/nlen
                    ans.extend([tuple(temp2)])

    ans = sort_similarities(ans)
    
    ansdic = {}

    # initialize each type as maybe match
    for i in ans:
        ansdic[i[0]] = MAYBE_MATCH

    cumul = 0
    for i in ans:
        # if this type is not found and should be maybe match
        if i[1] == 0 and i[2] == 0:
            continue
        # if still smaller after add, then add and assign the type as match
        if cumul + i[2] <= max_false_positives:
            ansdic[i[0]] = MATCH
            cumul = cumul + i[2]
        else:
            break

    cumul = 0
    for i in reversed(ans):
        if i[1] == 0 and i[2] == 0:
            continue
        if cumul + i[1] <= max_false_negatives:
            ansdic[i[0]] = NON_MATCH
            cumul = cumul + i[1]
        else:
            break

    return ansdic


def find_matches(
    max_false_positives,
    max_false_negatives,
    *,  # all arguments after this must be specified by keyword
    # (e.g. find_matches(0.1, 0.2, max_matches=10)
    max_matches=float("inf"),
    block_on_city=False,
):
    """
    Find matches between the PPP data and the OpenSecrets data.
    Inputs:
        max_false_positives (float): The maximum rate of false positives
            the classifier is allowed to have.
        max_false_negatives (float): The maximum rate of false negatives
            the classifier is allowed to have.
        max_matches (int): The maximum number of matches to return.
        block_on_city (bool): Whether or not to block on city when
            determining matches. Defaults to False.
    Returns:
        A list of tuples containing the OpenSecrets row, the PPP row,
        and the similarity classification of the match.
    """
    # TODO: Implement this function
    ans = []
    # Step 1) Train the classifier.
    label = train_classifier(max_false_positives, max_false_negatives)
    # Step 2) Load the PPP and OpenSecrets data.

    dfop = clean_opensecrets_data()
    dfppp = clean_ppp_data()

    dfop = { i.id:i for i in dfop}
    dfppp = { i.id:i for i in dfppp}

    # Step 3) Create a list of matches using your classifier as described in the README.
    #        If block_on_city is True, only consider matches where the city is the same.
    #        If the number of matches exceeds max_matches, stop searching.
    count = 0

    if block_on_city:
        for i in dfop.values():
            for j in dfppp.values():
                if i.city == j.city: #check if two tuples have the same city
                    result = calculate_similarity_tuple(i, j)
                    if label[result] == MATCH:
                        ans.append((i,j,result))
                        count = count + 1
                        if count >= max_matches:
                            return ans
    else:
        for i in dfop.values():
            for j in dfppp.values():
                result = calculate_similarity_tuple(i, j)
                if label[result] == MATCH:
                    print(result)
                    ans.append((i,j,result))
                    count = count + 1
                    if count >= max_matches:
                        return ans

    # Step 4) Return the list of matches.
from .datatypes import CleanedData, SimilarityTuple
import jellyfish


def calculate_similarity_tuple(tuple1, tuple2):
    """
    This function should take two tuples and return a similarity tuple
    describing the similarity of the two tuples.
    Inputs:
        tuple1: A CleanedData tuple
        tuple2: A CleanedData tuple
    Returns:
        A SimilarityTuple representing the similarity between the two
        data tuples.
    """
    # TODO: Implement this function
    score = [jellyfish.jaro_winkler_similarity(tuple1.org_name,tuple2.org_name),
             jellyfish.jaro_winkler_similarity(tuple1.city,tuple2.city)]
    answer = []
    for s in score[:2]:
        if s >= 0.95:
            answer.append('high')
        elif s >= 0.8:
            answer.append('medium')
        else:
            answer.append('low')

    if tuple1.zip == tuple2.zip:
        answer.append(True)
    else:
        answer.append(False)

    return SimilarityTuple(answer[0],answer[1],answer[2])
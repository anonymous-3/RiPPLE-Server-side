import itertools


def isNumber(inStr):
    try:
        val = int(inStr)
        return True
    except ValueError:
        return False


def combinations(iterable):
    """
        From https://stackoverflow.com/questions/464864/how-to-get-all-possible-combinations-of-a-list-s-elements
        Returns all combinations of the provided iterable (inclusive of subsets)
    """
    combinations = []
    for L in range(1, len(iterable) + 1):
        for subset in itertools.combinations(iterable, L):
            combinations.append(subset)
    return combinations


def topic_weights(question_topics):
    """
        Returns all topic weights for the given topics such that the weight is the topic_combination_length / total_topics
    """
    return [{
        "weight": len(x) / float(len(question_topics)),
        "topics": x
    } for x in combinations(question_topics)]

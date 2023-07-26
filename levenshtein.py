import Levenshtein


def get_LDN(word1: str, word2: str) -> float:
    """
    This function takes two words and returns their Levenshtein Distance Normalized (LDN)

    Parameters:
    - word1 (str): first word
    - word2 (str): second word

    Returns:
    float: LDN between the two words
    """

    return Levenshtein.distance(word1, word2) / max(len(word1), len(word2))


def calculate_LDN(word_list1: list[str], word_list2: list[str], average=True) -> float:
    """
    This function takes two lists of words and returns the optimal (minimum) 
    or average Levenshtein Distance Normalized (LDN)

    Parameters: 
    - word_list1 (list[str]): first list of words
    - word_list2 (list[str]): second list of words
    - average (boolean) : determines whether average or optimal is desired

    Returns:
    float: optimal/average LDN between the word lists
    """
    LDN_values = [get_LDN(word1, word2)
                  for word1 in word_list1 for word2 in word_list2]

    if average:
        return sum(LDN_values) / len(LDN_values)
    else:
        return min(LDN_values)


def get_closest_cognates(concept_from1: list[str], concept_from2: list[str]):
    LDN_values = [(get_LDN(word1, word2), word1, word2)
                  for word1 in concept_from1 for word2 in concept_from2 if word1 != 'XXX' and word2 != 'XXX']
    if not LDN_values:
        return None

    __, min_word1, min_word2 = min(LDN_values, key=lambda x: x[0])
    return min_word1, min_word2

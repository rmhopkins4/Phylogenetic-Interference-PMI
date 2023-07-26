from language import Language
from levenshtein import get_closest_cognates


def generate_potential_cognates(probably_related_languages: list[tuple[Language, Language]]) -> list:
    """
    Generates potential cognates between pairs of probably related languages.

    Parameters:
    - `probably_related_languages (list[tuple[Language, Language]])`: A list of language pairs, each represented as
            a tuple of two Language objects. These pairs are likely to be related languages or dialects.

    Returns:
    - `list (list[tuple[str, str]])`: A list containing the potential cognates between the words in the word lists of the probably related.
        Each element of the list is a tuple containing the two words considered as potential cognates.
    """
    potential_cognates = []

    for pairing in probably_related_languages:
        L1, L2 = pairing
        for concept1, concept2 in zip(L1.word_list, L2.word_list):
            cognate = get_closest_cognates(concept1, concept2)
            if cognate != None:
                potential_cognates.append(cognate)

    return potential_cognates

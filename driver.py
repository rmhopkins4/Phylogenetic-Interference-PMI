from dictionaryhandler import get_split_sets
from probably_related_generator import get_related_languages
from potential_cognates_generator import generate_potential_cognates
from language import Language
import align
import pmi_matrix_generator
from dERC_PMIcalculator import calculate_dERC_PMI
from dERC_LDNcalculator import calculate_dERC_LDN


import math
import random
import multiprocessing
import json

from scipy.optimize import minimize


def simple_dERC_LDN_test():
    """
    Perform a quick test to calculate the dERC between English and Standard German languages.

    This test function demonstrates the usage of the `'calculate_dERC_LDN'` method to compute the dERC/LDN distance
    between two languages. It builds dictionaries with families of languages, extracts the English and Standard German
    languages, and then calculates their dERC/LDN distance using the `'calculate_dERC_LDN'` function.

    The dERC/LDN distance reflects the evidence of relatedness between the two languages based on their word lists.

    Note:
        - The function requires the `'dictionaryhandler', 'dERC_LDNcalculator', and 'filehandler'` modules.
        - The `'build_dictionaries_with_families'` function is used to construct language dictionaries from provided text data.
        - The `'get_text'` function is used to retrieve text data from a file.

    Returns:
        None

    Example:
        Assuming the necessary modules and functions are available:

        >>> simple_dERC_LDN_test()
        Output: 0.5486910372997456 (value for ENGLISH and STANDARD_GERMAN)
    """
    from dictionaryhandler import build_dictionaries_with_families
    from dERC_LDNcalculator import calculate_dERC_LDN
    from filehandler import get_text

    full_set, common = build_dictionaries_with_families(
        get_text("./materials/lists.txt"))

    # Get English and Standard German languages
    L1 = [language
          for language in full_set['IE'] if language.name == 'ENGLISH'][0]
    L2 = [instance
          for instance in full_set['IE'] if instance.name == 'STANDARD_GERMAN'][0]

    print(calculate_dERC_LDN(L1, L2))


def save_sets(training_set, test_set):
    # Convert the sets to a JSON-serializable format
    serialized_training_set = {
        key: [language_obj.__dict__ for language_obj in value]
        for key, value in training_set.items()
    }
    serialized_test_set = {
        key: [language_obj.__dict__ for language_obj in value]
        for key, value in test_set.items()
    }

    # Save the data to files using JSON
    with open("./materials/training_set.json", 'w') as file:
        json.dump(serialized_training_set, file)
    with open("./materials/test_set.json", 'w') as file:
        json.dump(serialized_test_set, file)


def load_sets():
    # Load the data from files using JSON
    with open("./materials/training_set.json", 'r') as file:
        serialized_training_set = json.load(file)
    with open("./materials/test_set.json", 'r') as file:
        serialized_test_set = json.load(file)

    # Convert the JSON-serialized data to sets
    training_set = {
        key: [Language(**language_dict) for language_dict in value]
        for key, value in serialized_training_set.items()
    }
    test_set = {
        key: [Language(**language_dict) for language_dict in value]
        for key, value in serialized_test_set.items()
    }
    return training_set, test_set


# NOTE: NOW, my num_alignments (BOTH) counts valid (non '-') AND INVALID ones. I will have to test.
def objective_function(x):
    open_gap_score = x[0]
    extend_gap_score = x[1]
    theta_pmi = x[2]

    # training_set, test_set are defined
    # potential_cognates is defined
    # probably_related is defined
    # default_pmi_matrix is defined

    # build PMI matrix (training_set, cognates, theta_pmi, open_gap_score, extend_gap_score)
    pmi_matrix = pmi_matrix_generator.reestimate_pmi_matrix(
        potential_cognates,
        open_gap_score, extend_gap_score, theta_pmi,
        char_counts, num_characters,
        default_pmi_matrix.copy(), 11)  # 11 since the first is not re-estimating using probable cognates, its generating probable cognates for the first time.

    # score the 1,000 random pairs
    total_score = 0
    for related_pair in random_probably_related_language_pairs:
        total_score += calculate_dERC_PMI(
            related_pair[0], related_pair[1], pmi_matrix, open_gap_score, extend_gap_score)

    # average and return the scores (need to define dERC/PMI for languages first)
    mean_score = total_score / 1000
    print(f"mean dERC/PMI of the words: {mean_score}")
    return mean_score


if __name__ == '__main__':
    multiprocessing.freeze_support()

    # reset cached sets
    """
    training_set, test_set = get_split_sets()
    save_sets(training_set, test_set)
    # """

    # load cached training_set, test_set
    training_set, test_set = load_sets()

    # reset probably_related_languages
    """
    probably_related_languages = get_related_languages(
        training_set, test_set, theta_dERC=0.70)

    # Convert the list of tuples of Language objects to a JSON-serializable format
    serialized_data = [((language1.__dict__, language2.__dict__), )
                       for language1, language2 in probably_related_languages]
    # Save the data to a file using JSON
    with open("./materials/probably_related.json", 'w') as file:
        json.dump(serialized_data, file)
    # """

    # load cached probably_related_languages
    with open("./materials/probably_related.json", 'r') as file:
        serialized_data = json.load(file)
    # Convert the JSON data back to tuples of Language objects
    probably_related_languages = [(Language(**language1_dict), Language(**language2_dict))
                                  for ((language1_dict, language2_dict), ) in serialized_data]

    # reset potential_cognates
    """
    potential_cognates = generate_potential_cognates(
        probably_related_languages)
    with open("./materials/potential_cognates.json", 'w') as file:
        json.dump(potential_cognates, file)
    # """

    # load potential_cognates
    with open("./materials/potential_cognates.json", 'r') as file:
        potential_cognates = json.load(file)

    aligned_cognates = align.align_default(potential_cognates)

    # count: number of characters in training_list
    # count: p, b, f, v, m, w, 8, 4, t, d, s, z, c, n, r, l, S, Z, C, j, T, 5, y, k, g, x, N, q, G, X, h, 7, L, !, i, e, E, 3, a, u, o
    chars = ['p', 'b', 'f', 'v', 'm', 'w', '8', '4', 't', 'd', 's', 'z', 'c', 'n', 'r', 'l', 'S', 'Z', 'C', 'j',
             'T', '5', 'y', 'k', 'g', 'x', 'N', 'q', 'G', 'X', 'h', '7', 'L', '!', 'i', 'e', 'E', '3', 'a', 'u', 'o']
    num_characters = 0
    char_counts = {char: 0 for char in chars}
    for family in training_set.values():
        for lang in family:
            for concept in lang.word_list:
                for word in concept:
                    if word != 'XXX':
                        num_characters += len(word)
                        for char in word:
                            if char not in chars:
                                print(word)
                                continue
                            char_counts[char] += 1
    # now we have num_characters and char_counts

    # count: number of alignments total in aligned_cognates
    # count: each type of non-gap alignment in aligned_cognates
    num_alignments = 0
    valid_alignments_count = {}
    for aligned1, aligned2 in aligned_cognates:
        for char1, char2 in zip(aligned1, aligned2):
            num_alignments += 1
            # get valid alignments
            if char1 == '-' or char2 == '-':
                continue

            # make sure they are in sorted order
            char1, char2 = sorted([char1, char2])

            # Update the count in the dictionary
            valid_alignments_count[(char1, char2)] = \
                valid_alignments_count.get((char1, char2), 0) + 1

    # now we have num_valid_alignments and valid_alignments_count

    default_pmi_matrix = {}
    for (alignment_char1, alignment_char2), alignment_count in valid_alignments_count.items():
        default_pmi_matrix[(alignment_char1, alignment_char2)] = math.log((alignment_count / num_alignments) /
                                                                          (
            (char_counts[alignment_char1] / num_characters)
            * (char_counts[alignment_char2] / num_characters)
        ))

    """# pick my 1,000 matrices
    random_probably_related_language_pairs = random.sample(
        probably_related_languages, 1000)

    # get LDN score
    total_score = 0
    for related_pair in random_probably_related_language_pairs:
        total_score += calculate_dERC_LDN(related_pair[0], related_pair[1])
    print(total_score / 1000)

    # now actually optimize it bud.
    # initial guesses
    initial_guesses = [
        [-2.5, -1.8, 4.5],
        [-2.0, -1.0, 7.0],
        [-1.0, -0.5, 5.5],
        [-2.5, -1.8, 3.0],
        [-3.0, -2.0, 2.0],
    ]

    result = minimize(objective_function,
                      initial_guesses[0],
                      method='Nelder-Mead',
                      options={'initial_simplex': initial_guesses[1:]}
                      )

    # Print the optimized parameters and the corresponding objective function value
    optimal_params = result.x
    optimal_value = result.fun

    print("Optimized Parameters: ", optimal_params)
    print("Objective Function Value: ", optimal_value)"""

    # get it using values generated previously
    pmi_matrix = pmi_matrix_generator.reestimate_pmi_matrix(potential_cognates,
                                                            -2.4166728, -1.51569227, 5.59488733,
                                                            char_counts, num_characters,
                                                            default_pmi_matrix, 11)
    print(pmi_matrix)

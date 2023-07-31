import multiprocessing
from itertools import combinations
import matplotlib.pyplot as plt


from dERC_LDNcalculator import calculate_dERC_LDN
from language import Language


def __check_dERC_LDN_of_pairing(pairing: tuple[Language, Language]):
    """
    Calculates the dERC/LDN of a pair of languages and returns the pair if the distance is below a provided threshold.

    Parameters:
    - `pairing (tuple[Language, Language])`: A tuple containing two Language objects representing the pair of languages.
    - `theta_dERC (float, optional)`: The threshold value for dERC/LDN distance. If the calculated distance
            between the languages is below or equal to this value, the pair will be returned. Default is 0.70.

    Returns:
    - `tuple[Language, Language] or None`: If the dERC/LDN distance between the languages in the pairing is
            less than or equal to theta_dERC, returns the same input pairing. Otherwise, returns None.
    """
    L1, L2 = pairing
    dERC_of_pairing = calculate_dERC_LDN(L1, L2)
    return (pairing, dERC_of_pairing)


def get_related_languages(training_set: dict[str, list[Language]], test_set: dict[str, list[Language]], theta_dERC=.70):
    """
    Writes to a file a list of pairs of languages that are related, meaning their dERC/LDN is under the provided threshold.

    Parameters:
    - `training_set (dict)`: A dictionary containing language families as keys and lists of languages within each family as values.
            The language pairings will be sourced from here.
    - `test_set (dict)`: A dictionary containing language families as keys and lists of languages within each family as values.
            This parameter is required to enforce best practices by keeping the training_set and test_set separate yet together.
    - `theta_dERC` (float, optional): The threshold value for dERC/LDN distance. If the calculated distance between two languages
            is below or equal to this value, the pair will be considered related. Default is 0.70.

    Note:
    - The training_set and test_set should be organized as dictionaries where the keys represent language families (e.g., language families or language groups),
        and the values are lists of Language objects representing languages within each family.

    Example:
    ```
    training_set = {
        "IE": [Language("ENGLISH", [word_list]), Language("FRENCH", [word_list]), ...],
        ...
    }
    test_set = {
        "An": [Language("TAGALOG", "[word_list]"), Language("MALAY", "[word_list]"), ...],
        ...
    }
    write_related_languages(training_set, test_set, theta_dERC=0.65)
    # This will find language pairs with dERC/LDN distance less than or equal to 0.65 and save them to a file.
    ```
    """
    languages_list = [language  # Language class
                      for language_family in training_set.values()
                      for language in language_family]  # for language object in family

    probably_related_languages = []
    # Create a multiprocessing Pool with the number of CPU cores
    num_processes = multiprocessing.cpu_count()
    with multiprocessing.Pool(processes=num_processes) as pool:
        # Map the check_dERC_of_pairing function to the combinations of concept_lists_list
        results = pool.map(__check_dERC_LDN_of_pairing,
                           combinations(languages_list, 2))

        # Collect the results of probably related languages in probably_related_languages
        probably_related_languages = [
            pairing for pairing, score in results if score <= theta_dERC]

        scores = [score for pairing, score in results]

    # plot scoree
    plot_scores(scores)

    return probably_related_languages


def plot_scores(data_list: list[float]):
    """
    Plot the distribution of a list of floats.

    Parameters:
        data_list (list): A list of floats.

    Returns:
        None
    """
    # Check if data_list is not empty
    if not data_list:
        raise ValueError(
            "The input list is empty. Please provide a non-empty list of floats.")

    # Create the plot
    plt.figure(figsize=(8, 6))

    # Adjust the number of bins based on the size of the data
    num_bins = min(len(data_list) // 10, 50)

    # Create a histogram or density plot
    plt.hist(data_list, bins=num_bins, density=True,
             alpha=0.7, color='skyblue')

    # Add labels and title
    plt.xlabel("Values")
    plt.ylabel("Frequency")
    plt.title("Distribution Plot")

    # Show the plot
    plt.show()

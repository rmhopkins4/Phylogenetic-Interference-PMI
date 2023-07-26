import re
import random

from filehandler import get_text
from language import Language


def build_dictionaries_with_families(text: str) -> tuple[dict[str, list[Language]], dict[int, str]]:
    lines = text.strip().split('\n')

    # Find the indices of the language sections
    language_indices = [i for i, line in enumerate(
        lines) if "|" in line.strip()]

    # Extract the common words section
    common_words_section = lines[:language_indices[0]]

    # Build the dictionary for the 40 chosen words
    #   Currently, it is Swadesh number of word --> english word
    common_words = {}
    for line in common_words_section:
        parts = line.strip().split()
        if len(parts) != 2:
            continue
        number = parts[0].strip()
        word = parts[1].strip()
        common_words[int(number)] = word

    # Build dictionaries for each language
    languages = {}
    for i in range(len(language_indices)):
        start_index = language_indices[i]
        end_index = language_indices[i +
                                     1] if i < len(language_indices) - 1 else len(lines)
        language_section = lines[start_index:end_index]

        # Extract the language name from the first line
        language_name = language_section[0].split("{")[0].strip()
        language_family = language_section[0][language_section[0].find(
            "{")+1:language_section[0].find(".")]

        # Initialize the language list if it doesn't exist
        if language_family not in languages:
            languages[language_family] = []

        # Build the dictionary for the current language
        #   Currently, it is english word -> translated phonetic word
        language_words = {}
        for line in language_section[2:]:
            parts = line.strip().split()
            if len(parts) <= 3:  # Malformed / not what I'm looking for
                continue
            number = parts[0].strip()
            # no synonyms!!!
            phonetic = [re.sub(r'[^\w!]|(?!^)!', '', part)
                        for part in parts[2:] if re.sub(r'[^\w!]|(?!^)!', '', part)]
            language_words[int(number)] = phonetic

        # Add common words to the language dictionary
        filtered_language_words = [
            value for key, value in language_words.items() if key in common_words.keys()]
        languages[language_family].append(
            Language(language_name, filtered_language_words))

    return languages, common_words


def cull_languages(dictionary):
    illegal_strings = ["0", "1", "2", "6", "9", "W", "A", "B",
                       "D", "F", "H", "I", "J", "K", "M", "O",
                       "P", "Q", "R", "U", "V", "W", "Y", "\\", "ï", "½"]
    legal_chars = ['p', 'b', 'f', 'v', 'm', 'w', '8', '4', 't', 'd', 's', 'z', 'c', 'n', 'r', 'l', 'S', 'Z', 'C', 'j',
                   'T', '5', 'y', 'k', 'g', 'x', 'N', 'q', 'G', 'X', 'h', '7', 'L', '!', 'i', 'e', 'E', '3', 'a', 'u', 'o']

    families_to_remove = []

    # Create a copy of the dictionary keys
    family_names = list(dictionary.keys())

    for family_name in family_names:
        if family_name == "Oth":
            families_to_remove.append(family_name)
            continue

        languages_to_remove_in_family = []

        for language in dictionary[family_name]:
            if "PROTO" in language.name or "OLD" in language.name or language.name[-1].isdigit():
                languages_to_remove_in_family.append(language)
                continue

            all_words = [word for word_list in language.word_list
                         for word in word_list]

            # Check if any word contains illegal strings
            if any(illegal_string in word for illegal_string in illegal_strings for word in all_words):
                languages_to_remove_in_family.append(language)

            # Check if any character in the word is not a legal character
            if any(character not in legal_chars for word in all_words for character in word):
                languages_to_remove_in_family.append(language)

            # Check if there are more than 10 missing entries
            if all_words.count("XXX") >= 10:
                languages_to_remove_in_family.append(language)

        # Remove languages from the family
        for language in languages_to_remove_in_family:
            if language in dictionary[family_name]:
                dictionary[family_name].remove(language)

        # If the family has no remaining languages, mark it for removal
        if not dictionary[family_name]:
            families_to_remove.append(family_name)

    # Remove families from the dictionary
    for family in families_to_remove:
        dictionary.pop(family)

    return dictionary


def split_languages(dictionary):
    # Randomize the order of language families
    families = list(dictionary.keys())
    random.shuffle(families)

    total_languages = sum(len(family) for family in dictionary.values())
    half_total_languages = total_languages // 2

    group1 = {}
    group2 = {}
    count1 = 0

    # Go through each family in the randomized order
    for family in families:
        languages = dictionary[family]
        num_languages = len(languages)

        # Check if adding the family to group 1 exceeds the halfway point
        if count1 + num_languages <= half_total_languages:
            group1[family] = languages
            count1 += num_languages
        else:
            group2[family] = languages

    return group1, group2


def get_split_sets():
    """
    This function returns a training set and a testing set derived from the full set.
    The splitting is random, but language families are kept together.

    The word lists have been culled, so it does not contain every language from the base set.

    Returns:
    - training_set, test_set (tuple[dict, dict])

    This function is meant to be a one-stop-shop for a quick training and test set. 
    """
    # get full wordlist
    full_wordlist, common = build_dictionaries_with_families(
        get_text("materials/lists.txt"))
    full_wordlist = cull_languages(full_wordlist)

    # split wordlist into training set and test set (not super useful now lol)
    training_set, test_set = split_languages(full_wordlist)

    return training_set, test_set

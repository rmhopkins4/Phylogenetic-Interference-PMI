import bisect
import math
from itertools import product

from language import Language
from align import calculate_PMI


def calculate_dERC_PMI(L1: Language, L2: Language, pmi_matrix, open_gap_score, extend_gap_score) -> float:
    """
    Calculate the dERC/LDN (distance of Evidence of Relatedness using Levenshtein Distance Normalized)
    between two languages, L1 and L2, based on their word lists.

    Parameters:
    - L1 (Language): The first language to be compared.
    - L2 (Language): The second language to be compared.

    Returns:
    - float: The dERC/LDN distance between the two languages.
        0 <= distance <= 1

    Notes:
    - The word_list attribute of the Language class should contain a list of lists, where each inner list
          represents the words for a concept in the language.
    - This function calculates the distance between L1 and L2 using the Levenshtein Distance Normalized (LDN) measure.
    - The dERC/LDN distance reflects the evidence of relatedness between the two languages based on their word lists.
    - The function handles missing or incomplete word lists ('XXX' entries) to ensure accurate calculations.

    Algorithm Steps:
    1. Calculate LDN for on-diagonal entries (concepts in the same position) without 'XXX' entries.
        a. For word lists with multiple words for the same concept, the optimal (lowest) LDN is used.
    2. Calculate LDN for off-diagonal entries (pairwise combinations of concepts) without 'XXX' entries.
        a. For word lists with multiple words for the same concept, the average LDN is used.
    3. Calculate normalized ranks of LDN for on-diagonal entries.
    4. Calculate ER (Evidence of Relatedness) using the normalized ranks.
    5. Calculate ERC (Corrected Evidence of Relatedness) based on ER and the number of concepts (N).
    6. Calculate dERC (Distance based on Corrected Evidence of Relatedness) by normalizing ERC based on the maximum and minimum possible values (ERCmax and ERCmin).

    Examples:
    Assuming Language class has a word_list attribute, and you have two Language objects, L1 and L2:

    ```py
    L1 = Language("name1", [['cat', 'dog'], ['sun', 'moon']])
    L2 = Language("name2", [['hat', 'dog'], ['sun', 'mood']])
    distance = calculate_dERC_LDN(L1, L2)
    print(distance)  # Output could be 0.8315 (example value, actual value may vary).
    ```

    """

    L1_words: list[list[str]] = L1.word_list
    L2_words: list[list[str]] = L2.word_list

    # negative because normally bigger PMI is better but for LDN
    #   smaller is better so that's how it is calibrated

    on_diagonal = [(-1) * calculate_PMI(concepts1, concepts2, pmi_matrix, open_gap_score, extend_gap_score, average=False)
                   for concepts1, concepts2 in zip(L1_words, L2_words)
                   if 'XXX' not in concepts1 and 'XXX' not in concepts2]

    off_diagonal = [(-1) * calculate_PMI(concepts1, concepts2, pmi_matrix, open_gap_score, extend_gap_score, average=True)
                    for (i, concepts1), (j, concepts2) in product(enumerate(L1_words), enumerate(L2_words))
                    if i != j and 'XXX' not in concepts1 and 'XXX' not in concepts2]

    off_diagonal.sort()

    normalized_ranks = [__calculate_normalized_rank(diagonal_entry=diagonal,
                                                    off_diagonal_list=off_diagonal
                                                    ) for diagonal in on_diagonal]

    N = len(on_diagonal)

    # NOTE: this should never prock
    if N == 0:
        return 1

    ER = -sum(math.log(normalized_rank)
              for normalized_rank in normalized_ranks) / N

    Nmax = len(L1_words)  # should be 40 always
    ERmax = -(math.log(1 / ((Nmax * Nmax) - Nmax + 1)))
    ERmin = 0

    ERC = math.sqrt(N) * (ER - 1)
    ERCmax = math.sqrt(Nmax) * (ERmax - 1)
    ERCmin = math.sqrt(Nmax) * (ERmin - 1)

    dERC = (ERCmax - ERC) / (ERCmax - ERCmin)
    return dERC


def __calculate_normalized_rank(diagonal_entry: float, off_diagonal_list: list[float]) -> float:
    """
    Calculate the normalized rank for a diagonal entry in a matrix representation.

    This function calculates the normalized rank for a diagonal entry in a matrix represented by the 'off_diagonal_list'.
    The 'off_diagonal_list' must be sorted in ascending order.

    Parameters:
    - `diagonal_entry`: The diagonal entry for which the normalized rank needs to be calculated.
    - `off_diagonal_list (list)`: A sorted list of off-diagonal entries in the matrix.

    Returns:
    - `float`: The calculated normalized rank for the diagonal entry.

    Example:
    ```
    diagonal_entry = 5
    off_diagonal_list = [1, 3, 5, 7, 9]
    normalized_rank = __calculate_normalized_rank(diagonal_entry, off_diagonal_list)
    print(normalized_rank)  # Output: 0.3548350710659892 (example value, actual value may vary)
    ```
    """
    less_than_or_equal_count = bisect.bisect_right(
        off_diagonal_list, diagonal_entry)
    less_than_count = bisect.bisect_left(
        off_diagonal_list, diagonal_entry)

    total_entries = len(off_diagonal_list)
    normalized_rank = 1

    rank_count = less_than_or_equal_count - less_than_count + 1

    for value in range(less_than_count + 1, less_than_or_equal_count + 2):
        normalized_value = (value / (total_entries + 1)) ** (1 / rank_count)
        normalized_rank *= normalized_value

    return normalized_rank

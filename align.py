from Bio import pairwise2

from language import Language

import math

num = 10


def align_default(potential_cognates: list[tuple[str, str]]):
    aligned_cognates = []

    for cognate_pair in potential_cognates:
        word1, word2 = cognate_pair
        # Perform pairwise alignment using pairwise2.align.globalxx (simple match/mismatch-based alignment)
        alignments = pairwise2.align.globalxx(
            word1, word2, one_alignment_only=True)

        # Access alignment results
        if alignments:
            alignment = alignments[0]  # Consider the first alignment result
            aligned_word1, aligned_word2, _, _, _ = alignment
            aligned_cognates.append((aligned_word1, aligned_word2))

    return aligned_cognates


def align_w_prev_matrix(potential_cognates: list[tuple[str, str]], pmi_matrix: dict[tuple[str, str], float], open_gap_score: float, extend_gap_score: float):
    aligned_cognates = []

    for cognate_pair in potential_cognates:
        word1, word2 = cognate_pair
        alignments = pairwise2.align.globalcs(
            word1, word2,
            open=open_gap_score,
            extend=extend_gap_score,
            match_fn=lambda *args: custom_score(*args, pmi_matrix=pmi_matrix)
        )

        if alignments:
            alignment = alignments[0]  # Consider the first alignment result
            aligned_word1, aligned_word2, _, _, _ = alignment
            aligned_cognates.append((aligned_word1, aligned_word2))

    return aligned_cognates


def custom_score(match_char, ref_char, pmi_matrix: dict[tuple, float]):
    return pmi_matrix.get(tuple(sorted([match_char, ref_char])), 0)


# this is meant to align my potential cognates and get a PMI score
def get_PMI(potential_cognate1: str, potential_cognate2: str, pmi_matrix: dict[tuple, float], open_gap_score, extend_gap_score):
    alignments = pairwise2.align.globalcs(
        potential_cognate1, potential_cognate2, open=open_gap_score, extend=extend_gap_score, match_fn=lambda *args: custom_score(*args, pmi_matrix=pmi_matrix))
    if not alignments:
        print("Error in get_PMI(...)")
        print(potential_cognate1, potential_cognate2)
        return -200, (potential_cognate1, potential_cognate2)
    alignment = alignments[0]
    aligned_word1, aligned_word2, _, _, _ = alignment
    score = alignment.score
    return alignments[0].score, (aligned_word1, aligned_word2)


def calculate_PMI(word_list1, word_list2, pmi_matrix, open_gap_score, extend_gap_score, average=True):
    pmi_values = [get_PMI(word1, word2, pmi_matrix, open_gap_score, extend_gap_score)[0]
                  for word1 in word_list1 for word2 in word_list2]

    if average:
        return sum(pmi_values) / len(pmi_values)
    else:
        return max(pmi_values)

import align
import math
from collections import Counter


def reestimate_pmi_matrix(potential_cognates: list[tuple[str, str]], open_gap_score: float, extend_gap_score: float, theta_pmi: float, char_counts: dict, num_characters: int, current_pmi_matrix, num_remaining=10):
    print(f"number remaining: {num_remaining}")

    # pick out what will be used to reestimate
    cognate_pairs_moving_on = []
    aligned_cognate_pairs_moving_on = []

    # alignment cache for each loop
    alignment_cache = {}

    # align cognates (get probable cognates) using past pmi matrix
    for cognate_pair in potential_cognates:
        cognate_pair = tuple(sorted(cognate_pair))
        cache_key = tuple(cognate_pair)
        if cache_key not in alignment_cache:
            pair_pmi_score, (aligned_pair) = align.get_PMI(
                cognate_pair[0], cognate_pair[1],
                current_pmi_matrix,
                open_gap_score, extend_gap_score)
            alignment_cache[cache_key] = (pair_pmi_score, aligned_pair)
        else:

            pair_pmi_score, aligned_pair = alignment_cache[cache_key]

        if pair_pmi_score >= theta_pmi:
            # this is shipped off to next iteration
            cognate_pairs_moving_on.append(cognate_pair)
            # this is used to generate this PMI matrix
            aligned_cognate_pairs_moving_on.append(aligned_pair)

    # the probable cognates are be used to re-estimate the pmi_matrix
    num_alignments = 0
    valid_alignments_count = Counter()
    for aligned_pair in aligned_cognate_pairs_moving_on:
        word1, word2 = aligned_pair
        for char1, char2 in zip(word1, word2):
            num_alignments += 1
            if char1 == '-' or char2 == '-':
                continue

            char1, char2 = sorted([char1, char2])
            valid_alignments_count[(char1, char2)] += 1

    pmi_matrix = current_pmi_matrix
    for (alignment_char1, alignment_char2), alignment_count in valid_alignments_count.items():
        pmi_matrix[(alignment_char1, alignment_char2)] = math.log((alignment_count / num_alignments) /
                                                                  (
            (char_counts[alignment_char1] / num_characters)
            * (char_counts[alignment_char2] / num_characters)
        ))

    if num_remaining == 1:
        return pmi_matrix

    else:
        return reestimate_pmi_matrix(cognate_pairs_moving_on, open_gap_score, extend_gap_score, theta_pmi, char_counts, num_characters, pmi_matrix, num_remaining - 1)

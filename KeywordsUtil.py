import random


# Randomly Pick N keywords In given Frequency Range:
# p_min_freq: lower bound of frequency range
# p_max_freq: upper bound of frequency range
# p_n: number of keywords that is needed to pick
# return: [(word, count), ...]
def randomPickInFrequencyRange(p_db, p_min_freq, p_max_freq, p_n):
    results = p_db.queryLimitWordInCountOrderBy(p_min_freq, p_max_freq, p_n, 'random')
    return results


# Pick N nearest keywords to given frequency:
# p_freq: frequency target
# p_n: number of keywords that is needed to pick
# return: [(word, count), ...]
def pickNearestKeywordToFrequency(p_db, p_freq, p_n):
    results = p_db.queryLimitWordNearCount(p_freq, p_n)
    return results


# Pick lowest N keywords in given frequency range:
# p_min_freq: lower bound of frequency range
# p_max_freq: upper bound of frequency range
# p_n: number of keywords that is needed to pick
# return: [(word, count), ...]
def pickLowestInFrequencyRange(p_db, p_min_freq, p_max_freq, p_n):
    results = p_db.queryLimitWordInCountOrderBy(p_min_freq, p_max_freq, p_n, 'count')
    return results


def pickAllInFrequencyRange(p_db, p_min_freq, p_max_freq):
    results = p_db.queryWordInCount(p_min_freq, p_max_freq)
    return results


def randomPickInCurveGroup(p_db, p_group, p_n):
    results = p_db.queryLimitWordInCurveGroupOrderBy(p_group, p_n, 'random')
    return results


# Divide the frequency of keywords (> 1k) into 4 bins:
# [> 100k], total 64, sample 64
# [10k - 100k), total 927, sample 24
# [5k - 10k), total 793, sample 6
# [1k - 5k), total 4240, sample 6
def pick100keywords(p_db):
    l_keywords = []
    # [min_freq, max_freq, sample_number]
    l_bins = [[100000, 10000000, 64],
              [10000, 100000, 24],
              [5000, 10000, 6],
              [1000, 5000, 6]]
    for l_bin in l_bins:
        l_keywords.extend(randomPickInFrequencyRange(p_db, l_bin[0], l_bin[1], l_bin[2]))
    # shuffle the order of keywords
    random.shuffle(l_keywords)
    return l_keywords


# Pick all keywords within given frequency range
# p_db: database handle
# p_min_freq: lower bound of frequency range
# p_max_freq: upper bound of frequency range
# return: [w1, w2, w3, ...]
def pickInFrequencyRange(p_db, p_min_freq, p_max_freq):
    results = p_db.queryKeywords(p_min_freq, p_max_freq)
    return results

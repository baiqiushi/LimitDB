import Conf
import random
import DatabaseFactory

database = Conf.DATABASE
db = DatabaseFactory.getDatabase(database)


def clean():
    db.close()


# Randomly Pick N keywords In given Frequency Range:
# p_min_freq: lower bound of frequency range
# p_max_freq: upper bound of frequency range
# p_n: number of keywords that is needed to pick
# return: [(word, count), ...]
def randomPickInFrequencyRange(p_min_freq, p_max_freq, p_n):
    results = db.queryLimitWordInCountOrderBy(p_min_freq, p_max_freq, p_n, 'random')
    return results


# Pick N nearest keywords to given frequency:
# p_freq: frequency target
# p_n: number of keywords that is needed to pick
# return: [(word, count), ...]
def pickNearestKeywordToFrequency(p_freq, p_n):
    results = db.queryLimitWordNearCount(p_freq, p_n)
    return results


# Pick lowest N keywords in given frequency range:
# p_min_freq: lower bound of frequency range
# p_max_freq: upper bound of frequency range
# p_n: number of keywords that is needed to pick
# return: [(word, count), ...]
def pickLowestInFrequencyRange(p_min_freq, p_max_freq, p_n):
    results = db.queryLimitWordInCountOrderBy(p_min_freq, p_max_freq, p_n, 'count')
    return results


# Divide the frequency of keywords (> 1k) into 4 bins:
# [> 100k], total 64, sample 64
# [10k - 100k), total 927, sample 24
# [5k - 10k), total 793, sample 6
# [1k - 5k), total 4240, sample 6
def pick100keywords():
    l_keywords = []
    # [min_freq, max_freq, sample_number]
    l_bins = [[100000, 10000000, 64],
              [10000, 100000, 24],
              [5000, 10000, 6],
              [1000, 5000, 6]]
    for l_bin in l_bins:
        l_keywords.extend(randomPickInFrequencyRange(l_bin[0], l_bin[1], l_bin[2]))
    # shuffle the order of keywords
    random.shuffle(l_keywords)
    return l_keywords


def test():
    print pickNearestKeywordToFrequency(3000000, 1)

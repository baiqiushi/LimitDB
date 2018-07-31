from MySQLUtil import MySQLUtil
import random

db = MySQLUtil()


def clean():
    db.close()


# Randomly Pick N keywords In given Frequency Range:
# p_min_freq: lower bound of frequency range
# p_max_freq: upper bound of frequency range
# p_n: number of keywords that is needed to pick
# return: [(word, count), ...]
def randomPickInFrequencyRange(p_min_freq, p_max_freq, p_n):
    l_sql = 'SELECT p.word, p.count FROM ' \
            '  (SELECT t.word, t.count FROM limitdb.wordcount t ' \
            '    WHERE t.count >= ' + str(p_min_freq) + \
            '      and t.count < ' + str(p_max_freq) + \
            '  ) p ORDER BY RAND() ' \
            'LIMIT ' + str(p_n)
    results = db.query(l_sql)
    return results


# Pick N nearest keywords to given frequency:
# p_freq: frequency target
# p_n: number of keywords that is needed to pick
# return: [(word, count), ...]
def pickNearestKeywordToFrequency(p_freq, p_n):
    l_sql = 'SELECT p.word, p.count FROM ' \
            '  (SELECT t.word, t.count FROM limitdb.wordcount t ' \
            '    WHERE t.count >= ' + str(p_freq / 2) + \
            '      and t.count < ' + str(p_freq * 2) + \
            '  ) p ORDER BY ABS(p.count - ' + str(p_freq) + ') ' \
            'LIMIT ' + str(p_n)
    results = db.query(l_sql)
    return results


# Pick lowest N keywords in given frequency range:
# p_min_freq: lower bound of frequency range
# p_max_freq: upper bound of frequency range
# p_n: number of keywords that is needed to pick
# return: [(word, count), ...]
def pickLowestInFrequencyRange(p_min_freq, p_max_freq, p_n):
    l_sql = 'SELECT p.word, p.count FROM ' \
            '  (SELECT t.word, t.count FROM limitdb.wordcount t ' \
            '    WHERE t.count >= ' + str(p_min_freq) + \
            '      and t.count < ' + str(p_max_freq) + \
            '  ) p ORDER BY count ' \
            'LIMIT ' + str(p_n)
    results = db.query(l_sql)
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

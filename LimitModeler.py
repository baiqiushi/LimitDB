import time
import numpy as np
import csv

import DatabaseFactory
import KeywordsUtil

database = 'MySQL'
tableName = 'coordtweets'
# Resolution of image
res_x = 1920/4
res_y = 1080/4

# Keywords frequency range
min_freq = 2000000
max_freq = 4000000

# Target Quality
Q0 = 0.85


def hashByNumpy(ar, r=((-170, -60), (15, 70))):
    H, x, y = np.histogram2d(ar[:, 0], ar[:, 1], bins=(res_x, res_y), range=r)
    return H


# Build Limit Model
# quality function is perceptual hash
# retrieve whole results once into memory then find the target K0 and corresponding ratio
def buildModel(p_database, p_tableName, p_min_freq, p_max_freq):

    db = DatabaseFactory.getDatabase(p_database)

    l_min_freq = int(p_min_freq)
    l_max_freq = int(p_max_freq)

    keywords = KeywordsUtil.pickLowestInFrequencyRange(l_min_freq, l_max_freq, 2000)

    # [word, count, k, ratio, quality]
    keyword_models = []

    t = time.time()
    if len(keywords) > 0:
        for keyword in keywords:
            t0 = time.time()
            # create perfect image of the file
            ar = np.array(db.GetCoordinate(p_tableName, keyword[0], -1))
            if len(ar) == 0:
                continue
            t1 = time.time()
            H = hashByNumpy(ar)
            perfectLen = np.count_nonzero(H)
            i = 0.0
            low = 0.0
            high = 100.0
            similarity = 0.0
            iterTimes = 0
            t2 = time.time()
            while (similarity < Q0 or similarity > Q0 + 0.01) and iterTimes < 10:
                # binary search for the target K0 for target quality 0.85
                if similarity < Q0:
                    low = i
                    i = (high + i) / 2
                else:
                    high = i
                    i = (i + low) / 2
                k = int(i * len(ar) / 100)
                Hs = hashByNumpy(ar[:k])
                sampleLen = np.count_nonzero(Hs)
                similarity = float(sampleLen) / perfectLen
                iterTimes += 1
            print keyword[0], \
                "quality:", similarity, \
                "k:", k, \
                "ratio:", i, \
                "fetch:", t1 - t0, \
                "draw:", t2 - t1, \
                "search:", time.time() - t2
            keyword_models.append([keyword[0], keyword[1], k, i, similarity])

    with open('keyword_models.csv', 'w') as csvFile:
        csvWriter = csv.writer(csvFile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for line in keyword_models:
            csvWriter.writerow(line)
    print "Total time of", p_tableName, ":", time.time() - t


print '================================================='
print '  ' + database + '  Experiments - 4.1 Limit Modeling'
print '================================================='
print 'table: ', tableName
print 'frequency range: [', min_freq, ', ', max_freq, ']'
print 'resolution: ', res_x, 'x', res_y
print 'target quality [Q0]: ', Q0
print '-------------------------------------------------'
buildModel(database, tableName, min_freq, max_freq)

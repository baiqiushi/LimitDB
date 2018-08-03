import csv
import time

import Conf
import numpy as np
import DatabaseFactory


# Common config
import KeywordsUtil

database = Conf.DATABASE
tableName = Conf.TABLE

# Config for this experiment
csvFileName = 'keyword_curves.csv'
# Resolution of image
res_x = 1920/4
res_y = 1080/4

# Keywords frequency range
min_freq = 5000
max_freq = 4000000

# k value percentage of the keyword frequency
# 5 - 100, step = 5
k_percentages = range(5, 100, 5)


def hashByNumpy(ar, r=((-170, -60), (15, 70))):
    H, x, y = np.histogram2d(ar[:, 0], ar[:, 1], bins=(res_x, res_y), range=r)
    return H


def generateCurves(p_database, p_tableName, p_min_freq, p_max_freq):
    db = DatabaseFactory.getDatabase(p_database)

    l_min_freq = int(p_min_freq)
    l_max_freq = int(p_max_freq)

    keywords = KeywordsUtil.pickAllInFrequencyRange(l_min_freq, l_max_freq)

    t = time.time()
    with open(csvFileName, 'w') as csvFile:
        csvWriter = csv.writer(csvFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        progress = 0
        skipped = 0
        for keyword in keywords:
            progress += 1
            curve = []
            curve.extend(keyword)
            t0 = time.time()
            # 1. create perfect image of this keyword
            ar = np.array(db.GetCoordinate(p_tableName, keyword[0], -1))
            if len(ar) == 0:
                skipped += 1
                continue
            if len(ar) != keyword[1]:
                print '[' + keyword[0] + ']', 'frequency = ' + str(keyword[1]) + ', len(perfect) = ' + str(len(ar))
            t1 = time.time()
            H = hashByNumpy(ar)
            perfectLen = np.count_nonzero(H)
            t2 = time.time()
            # 2. for each k percentage calculate the quality value
            for k_percentage in k_percentages:
                k = int(k_percentage * len(ar) / 100)
                Hs = hashByNumpy(ar[:k])
                sampleLen = np.count_nonzero(Hs)
                similarity = float(sampleLen) / perfectLen
                curve.append(similarity)
            t3 = time.time()
            # 3. write down the curve of this keyword to csv file
            # [keyword, frequency, q(5%), q(10%), ......, q(95%)]
            csvWriter.writerow(curve)
            t4 = time.time()
            # 4. output time information to console
            print keyword[0], \
                ", [freq]", keyword[1], \
                ", [query]", t1 - t0, \
                ", [perfect]", t2 - t1, \
                ", [curve]", t3 - t2, \
                ", [write]", t4 - t3, \
                ", [total]", time.time() - t0, \
                ", [All]", time.time() - t, \
                ", [progress]", str(progress * 100 / len(keywords)) + '%'

    return len(keywords) - skipped


print '================================================='
print '  ' + database + '  Experiments - 4.1 Curve Generating'
print '================================================='
print 'table:', tableName
print 'frequency range:[', min_freq, ',', max_freq, ']'
print 'resolution:', res_x, 'x', res_y
print 'k_percentage:', map(lambda k_p: str(k_p) + '%', k_percentages)
print '-------------------------------------------------'
start = time.time()
count = generateCurves(database, tableName, min_freq, max_freq)
end = time.time()
print '================================================='
print '  ' + database + '  Results - 4.1 Curve Generating'
print '================================================='
print 'table:', tableName
print 'frequency range:[', min_freq, ',', max_freq, ']'
print 'resolution:', res_x, 'x', res_y
print 'k_percentage:', map(lambda k_p: str(k_p) + '%', k_percentages)
print '-------------------------------------------------'
print 'Finished!', count, 'keywords processed,', end - start, 'seconds spent.'

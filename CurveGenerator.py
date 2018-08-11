import csv
import time
import KeywordsUtil
import Conf
import DatabaseFactory
import QualityUtil


# Common config
database = Conf.DATABASE
tableName = Conf.TABLE

# Config for this experiment
csvFileName = 'keyword_curves.csv'


# Keywords frequency range
min_freq = 5000
max_freq = 4000000

# k value percentage of the keyword frequency
# 5 - 100, step = 5
k_percentages = range(5, 100, 5)


def generateCurves(p_min_freq, p_max_freq):
    db = DatabaseFactory.getDatabase(database)

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

            # 1. Get total coordinates of this keyword
            t0 = time.time()
            totalCoordinates = db.GetCoordinate(tableName, keyword[0], -1)
            if len(totalCoordinates) == 0:
                skipped += 1
                continue
            if len(totalCoordinates) != keyword[1]:
                print '[' + keyword[0] + ']', \
                    'frequency = ' + str(keyword[1]) + ', len(perfect) = ' + str(len(totalCoordinates))

            # 2. for each k percentage calculate the quality value
            t1 = time.time()
            for k_percentage in k_percentages:
                similarity = QualityUtil.phQualityOfKPercentage(totalCoordinates, k_percentage)
                curve.append(similarity)

            # 3. write down the curve of this keyword to csv file
            # [keyword, frequency, q(5%), q(10%), ......, q(95%)]
            t2 = time.time()
            csvWriter.writerow(curve)
            t3 = time.time()
            # 4. output time information to console
            print keyword[0], \
                ", [freq]", keyword[1], \
                ", [query]", t1 - t0, \
                ", [curve]", t2 - t1, \
                ", [write]", t3 - t2, \
                ", [total]", time.time() - t0, \
                ", [All]", time.time() - t, \
                ", [progress]", str(progress * 100 / len(keywords)) + '%'

    return len(keywords) - skipped


print '================================================='
print '  ' + database + '  Experiments - 4.1 Curve Generating'
print '================================================='
print 'table:', tableName
print 'frequency range:[', min_freq, ',', max_freq, ']'
print 'k_percentage:', map(lambda k_p: str(k_p) + '%', k_percentages)
QualityUtil.printInfo()
print '-------------------------------------------------'
start = time.time()
count = generateCurves(min_freq, max_freq)
end = time.time()
print '================================================='
print '  ' + database + '  Results - 4.1 Curve Generating'
print '================================================='
print 'table:', tableName
print 'frequency range:[', min_freq, ',', max_freq, ']'
print 'k_percentage:', map(lambda k_p: str(k_p) + '%', k_percentages)
QualityUtil.printInfo()
print '-------------------------------------------------'
print 'Finished!', count, 'keywords processed,', end - start, 'seconds spent.'

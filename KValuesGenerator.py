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
csvFileName_k_values = 'keyword_k_values.csv'
csvFileName_k_ratios = 'keyword_k_ratios.csv'


# Keywords frequency range
min_freq = 5000
max_freq = 4000000

# target qualities
qualities = range(70, 100, 5)


def generateKValues(p_min_freq, p_max_freq):
    db = DatabaseFactory.getDatabase(database)

    l_min_freq = int(p_min_freq)
    l_max_freq = int(p_max_freq)

    keywords = KeywordsUtil.pickAllInFrequencyRange(l_min_freq, l_max_freq)

    t = time.time()
    with open(csvFileName_k_values, 'w') as csvFile_k_values:
        with open(csvFileName_k_ratios, 'w') as csvFile_k_ratios:
            csvWriter_k_values = csv.writer(csvFile_k_values, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csvWriter_k_ratios = csv.writer(csvFile_k_ratios, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

            progress = 0
            skipped = 0
            for keyword in keywords:
                progress += 1
                k_values = []
                k_ratios = []
                k_values.extend(keyword)
                k_ratios.extend(keyword)

                # 1. Get total coordinates of this keyword
                t0 = time.time()
                totalCoordinates = db.GetCoordinate(tableName, keyword[0], -1)
                if len(totalCoordinates) == 0:
                    skipped += 1
                    continue
                if len(totalCoordinates) != keyword[1]:
                    print '[' + keyword[0] + ']', \
                        'frequency = ' + str(keyword[1]) + ', len(perfect) = ' + str(len(totalCoordinates))

                # 2. for each target quality calculate the k value using binary search
                t1 = time.time()
                for quality in qualities:
                    k, kp = QualityUtil.findKOfQuality(totalCoordinates, float(quality)/100.0)
                    k_values.append(k)
                    k_ratios.append(kp)

                # 3. write down the k_values / k_ratios of this keyword to csv file
                # [keyword, frequency, k(0.7), k(0.75), ......, k(0.95)]
                # [keyword, frequency, kp(0.7), kp(0.75), ......, kp(0.95)]
                t2 = time.time()
                csvWriter_k_values.writerow(k_values)
                csvWriter_k_ratios.writerow(k_ratios)
                t3 = time.time()
                # 4. output time information to console
                print keyword[0], \
                    ", [freq]", keyword[1], \
                    ", [query]", t1 - t0, \
                    ", [k_values/ratios]", t2 - t1, \
                    ", [write]", t3 - t2, \
                    ", [total]", time.time() - t0, \
                    ", [All]", time.time() - t, \
                    ", [progress]", str(progress * 100 / len(keywords)) + '%'

    return len(keywords) - skipped


print '================================================='
print '  ' + database + '  Experiments - 4.3 K Values Generating'
print '================================================='
print 'table:', tableName
print 'frequency range:[', min_freq, ',', max_freq, ']'
print 'target qualities:', map(lambda quality: str(quality) + '%', qualities)
QualityUtil.printInfo()
print '-------------------------------------------------'
start = time.time()
count = generateKValues(min_freq, max_freq)
end = time.time()
print '================================================='
print '  ' + database + '  Results - 4.2 K Values Generating'
print '================================================='
print 'table:', tableName
print 'frequency range:[', min_freq, ',', max_freq, ']'
print 'target qualities:', map(lambda quality: str(quality) + '%', qualities)
QualityUtil.printInfo()
print '-------------------------------------------------'
print 'Finished!', count, 'keywords processed,', end - start, 'seconds spent.'

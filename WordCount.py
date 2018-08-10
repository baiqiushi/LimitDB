import csv
import Conf
import DatabaseFactory
import KeywordsUtil
import time


database = Conf.DATABASE
tableName = Conf.TABLE

# Keywords frequency range
min_freq = 5000
max_freq = 4000000

db = DatabaseFactory.getDatabase(database)


def collectWordsCounts():
    keywords = KeywordsUtil.pickAllInFrequencyRange(min_freq, max_freq)
    csvFileName = 'wordcount.csv'
    with open(csvFileName, 'w') as csvFile:
        csvWriter = csv.writer(csvFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        progress = 0
        t0 = time.time()
        for keyword in keywords:
            count = db.GetCount(tableName, keyword[0])
            csvWriter.writerow([keyword[0], count])
            progress += 1
            t1 = time.time()
            print "Total time:", t1 - t0, "Progress:", str(progress * 100 / len(keywords)) + '%'


# collectWordsCounts()

print db.GetCount(tableName, 't-storm')

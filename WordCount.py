import csv
import Conf
import DatabaseFactory
import KeywordsUtil
import time
from collections import Counter
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords')

database = Conf.DATABASE
tableName = Conf.TABLE

# Keywords frequency range
min_freq = 5000
max_freq = 4000000

limit = 1000000


# select count(*) from limitdb.coord_tweets where ftcontains(text, keyword);
# collect all these cardinalities for each keyword
def collectWordsCardinalities():
    db = DatabaseFactory.getDatabase(database)
    keywords = KeywordsUtil.pickAllInFrequencyRange(min_freq, max_freq)
    csvFileName = 'wordcardinality.csv'
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


def collectWordCountForAsterixDB(p_limit):
    db = DatabaseFactory.getDatabase('AsterixDB')
    csvFileName = 'wordcount.csv'
    wordcount = Counter()

    # 1. get the cardinality of the whole table
    print "[1] Get the cardinality of the whole table ......"
    sql = "select count(*) as count from limitdb." + tableName
    results = db.query(sql)
    tableCardinality = results[0]['count']

    # 2. traverse the whole table by limit and offset and count tokens
    print "[2] Traverse the whole table by limit and offset and count tokens ......"
    progress = 0
    t0 = time.time()
    for offset in range(0, tableCardinality, p_limit):
        sql = "select word_tokens(t.text) as tokens from limitdb." + tableName + \
              " t limit " + str(p_limit) + " offset " + str(offset)
        # [{'tokens': ['t1', 't2']}, {'tokens':['t3', 't4', 't5']}]
        results = db.query(sql)
        for record in results:
            # get rid of stop words
            tokens = [word for word in record['tokens'] if word not in stopwords.words('english') and len(word) > 2]
            wordcount.update(Counter(tokens))

        progress += p_limit
        t1 = time.time()
        print "Total time:", t1 - t0, "Progress:", str(float(progress) * 100 / float(tableCardinality)) + '%'

    # 3. write to csv file
    print "[3] Writing wordcount dictionary into csv file", csvFileName, "......"
    with open(csvFileName, 'w') as csvFile:
        csvWriter = csv.writer(csvFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for key, value in sorted(wordcount.iteritems(), key=lambda (k, v): (v, k), reverse=True):
            csvWriter.writerow([key, value])
        # for key in wordcount.keys():
        #     csvWriter.writerow([key, wordcount[key]])


print '================================================='
print '     Experiments - Word Count for AsterixDB'
print '================================================='
print 'table:', tableName
print 'One time limit:', limit
print '================================================='
start = time.time()
collectWordCountForAsterixDB(limit)
end = time.time()
print '-------------------------------------------------'
print 'Word Count for AsterixDB is done!'
print 'Total time:', end - start

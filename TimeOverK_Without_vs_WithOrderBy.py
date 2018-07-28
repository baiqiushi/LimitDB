from MySQLUtil import MySQLUtil
import copy
import random
import time
import KeywordsUtil


database = 'MySQL'
tableName = 'coordtweets'
orderBy = 'id'
num_runs = 2
dummy_sql = 'select count(1) from (select t.text from limitdb.dummy_table t where t.id < 865350497200371700) p ' \
                    'where p.text like \'%lo%\' '
frequencyLevels = [100000, 200000, 300000, 400000, 500000, 600000, 700000, 800000, 900000, 1000000, 2000000, 3000000]
# k value percentage of the keyword frequency
k_percentages = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

# For each frequency level 100k, 200k, 300k, 400k, 500k, 600k, 700k, 800k, 900k, 1m
# Pick one keyword
# keywords = [(word, count), ...]
keywords = []
for frequencyLevel in frequencyLevels:
    keywords.extend(KeywordsUtil.pickNearestKeywordToFrequency(frequencyLevel, 1))


def execTimeLimitK(p_db, p_tableName, p_keyword, p_k):
    # print 'sending limit ' + str(p_k) + ' query for keyword: ' + p_keyword
    # send limit k query to db
    start = time.time()
    p_db.queryLimit(p_tableName, p_keyword, p_k)
    end = time.time()
    return end - start


def execTimeLimitKAndOrderBy(p_db, p_tableName, p_keyword, p_k, p_orderBy):
    # print 'sending limit ' + str(p_k) + 'and order by ' + p_orderBy + ' query for keyword: ' + p_keyword
    # send limit k and order by query to db
    start = time.time()
    p_db.queryLimitOrderBy(p_tableName, p_keyword, p_k, p_orderBy)
    end = time.time()
    return end - start


def run(p_database, p_tableName, p_withOrderBy):

    if p_database == 'MySQL':
        db = MySQLUtil()
    else:
        print 'Database: ', p_database, ' is not supported now!'
        return

    # [k, avg_time(word[1]), avg_time(word[2]), ..., avg_time(word[N])]
    execTime_All = []
    shuffled_keywords = copy.deepcopy(keywords)
    for k_percent in k_percentages:
        execTime_k = [k_percent]
        # sum_runs = {word1: time, word2: time, ...}
        sum_runs = {}
        # Average several runs
        for i in range(num_runs):
            print 'k percentage ==== ', str(k_percent), '  running ', str(i + 1)
            # restart the MySQL server
            db.restart()

            # send dummy queries to warm up the database
            startT = time.time()
            db.query(dummy_sql)
            endT = time.time()
            print 'dummy query takes ', str(endT - startT), ' seconds.'

            # every run shuffle the order of querying keywords
            random.shuffle(shuffled_keywords)
            # (word, count)
            for keyword in shuffled_keywords:
                k = int(round(keyword[1] * k_percent))
                if p_withOrderBy:
                    execTime = execTimeLimitKAndOrderBy(db, p_tableName, keyword[0], k, orderBy)
                else:
                    execTime = execTimeLimitK(db, p_tableName, keyword[0], k)
                if keyword[0] in sum_runs:
                    sum_runs[keyword[0]] += execTime
                else:
                    sum_runs[keyword[0]] = execTime

        # print sum_runs
        # Use defined order of keywords to store the average execution time
        for keyword in keywords:
            # print 'sums of [', keyword[0], '] = ', str(sum_runs[keyword[0]])
            execTime_k.extend([sum_runs[keyword[0]] / num_runs])

        execTime_All.append(execTime_k)

    return execTime_All


def print_execTime(execTime):
    for line in execTime:
        s_arr = [str(a) for a in line]
        print ', '.join(s_arr)


print '================================================='
print '  ' + database + '  Experiments - 3.1 Time of limit K'
print '================================================='
print 'table: ', tableName
print 'keywords: ', keywords
print 'K values: ', k_percentages
print '-------------------------------------------------'

execTime_without_orderBy = run(database, tableName, False)

print '================================================='
print '  ' + database + '  Results - 3.1 Time of limit K'
print '================================================='
print 'table: ', tableName
print 'keywords: ', keywords
print 'K values: ', k_percentages
print '-------------------------------------------------'
print_execTime(execTime_without_orderBy)

print '================================================='
print '  ' + database + '  Experiments - 3.2 Time of limit K & order by ' + orderBy
print '================================================='
print 'table: ', tableName
print 'keywords: ', keywords
print 'K values: ', k_percentages
print '-------------------------------------------------'

execTime_with_orderBy = run(database, tableName, True)

print '================================================='
print '  ' + database + '  Experiments - 3.2 Results of limit K & order by ' + orderBy
print '================================================='
print 'table: ', tableName
print 'keywords: ', keywords
print 'K values: ', k_percentages
print '-------------------------------------------------'

print_execTime(execTime_with_orderBy)

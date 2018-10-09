import DatabaseFactory
import Conf
import time
import math
from sets import Set


# Common config
database = Conf.DBTYPE
tableName = Conf.TABLE
keywords = ['job', 'water', 'soccer']


# p_limit1 < p_limit2, check whether p_limit1 is subset of p_limit2
def isSubsetFromDB(p_db, p_tableName, p_keyword, p_limit1, p_limit2):
    queryTime = 0
    # query p_limit1 set
    start = time.time()
    set1 = Set(p_db.GetID(p_tableName, p_keyword, p_limit1))
    end = time.time()
    queryTime += (end - start)
    # restart database
    start = time.time()
    # p_db.restart()
    end = time.time()
    print 'wait for ', str(end - start), ' seconds for db to restart'
    # query p_limit2 set
    start = time.time()
    set2 = Set(p_db.GetID(p_tableName, p_keyword, p_limit2))
    end = time.time()
    queryTime += (end - start)
    print 'DB query time: ', queryTime, ' s'
    # Debug #
    # print '-------------------------------------'
    # print set1
    # print '-------------------------------------'
    # print '-------------------------------------'
    # print set2
    # print '-------------------------------------'
    # Debug #
    start = time.time()
    res = set1.issubset(set2)
    end = time.time()
    print 'Computation time: ', (end - start), ' s'
    if res:
        return True
    else:
        return False


def testSubsetForKeyword(p_db, p_tableName, p_keyword):
    print 'Table: ' + p_tableName
    print 'Keyword: ' + p_keyword

    failed_cases = []
    for k in [1, 10, 100, 1000, 10000, 50000, 100000, 500000, 1000000, 2000000]:
        for delta_k in [1, math.ceil(0.1*k), math.ceil(0.3*k), math.ceil(0.5*k)]:
            result = isSubsetFromDB(p_db, p_tableName, p_keyword, int(k), int(k + delta_k))
            msg = 'Checking whether limit ' + str(int(k)) + ' is subset of limit ' + str(int(k + delta_k))
            if result:
                print msg + ' --- YES'
            else:
                failed_cases.append([int(k), int(k + delta_k)])

    if len(failed_cases) > 0:
        print '***********************************************'
        print 'Failed limit k pairs:'
        for failure in failed_cases:
            print '[' + failure[0] + ', ' + failure[1] + ']'


print '================================================='
print '  ' + database + '  Experiments - 2 Test Subset'
print '================================================='

db = DatabaseFactory.getDatabase(database)

for keyword in keywords:
    testSubsetForKeyword(db, tableName, keyword)
    print '------------------------------------------------'

db.close()

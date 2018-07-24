import numpy as np
import MySQLUtil as db
# import time
import math

database = 'MySQL'
tableName = 'coordtweets'
keywords = ['job', 'water', 'soccer']


# p_limit1 < p_limit2, check whether p_limit1 is subset of p_limit2
def isSubsetFromDB(p_tableName, p_keyword, p_limit1, p_limit2):
    # start = time.time()
    ar1 = np.array(db.GetCoordinate(p_tableName, p_keyword, p_limit1))
    ar2 = np.array(db.GetCoordinate(p_tableName, p_keyword, p_limit2))
    # end = time.time()
    # print 'DB query time: ', (end - start), ' s'
    # start = time.time()
    for c in ar1:
        if c not in ar2:
            return False
    # end = time.time()
    # print 'Computation time: ', (end - start), ' s'
    return True


def testSubsetForKeyword(p_tableName, p_keyword):
    print 'Table: ' + p_tableName
    print 'Keyword: ' + p_keyword

    failed_cases = []
    for k in [1, 10, 100, 1000, 10000, 50000, 100000, 500000, 1000000, 2000000]:
        for delta_k in [1, math.ceil(0.1*k), math.ceil(0.3*k), math.ceil(0.5*k)]:
            result = isSubsetFromDB(p_tableName, p_keyword, int(k), int(k + delta_k))
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

for keyword in keywords:
    testSubsetForKeyword(tableName, keyword)
    print '------------------------------------------------'

db.close()

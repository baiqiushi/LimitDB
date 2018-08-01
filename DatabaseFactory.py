from MySQLUtil import MySQLUtil
from AsterixDBUtil import AsterixDBUtil


def getDatabase(p_database):
    if p_database == 'MySQL':
        db = MySQLUtil()
        return db
    elif p_database == 'AsterixDB':
        db = AsterixDBUtil()
        return db
    else:
        print 'Database: ', p_database, ' is not supported now!'
        return

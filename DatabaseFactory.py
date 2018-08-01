from MySQLUtil import MySQLUtil
from AsterixDBUtil import AsterixDBUtil
from PostgreSQLUtil import PostgreSQLUtil


def getDatabase(p_database):
    if p_database == 'MySQL':
        db = MySQLUtil()
        return db
    elif p_database == 'AsterixDB':
        db = AsterixDBUtil()
        return db
    elif p_database == 'PostgreSQL':
        db = PostgreSQLUtil()
        return db
    else:
        print 'Database: ', p_database, ' is not supported now!'
        return

# from MySQLUtil import MySQLUtil
from AsterixDBUtil import AsterixDBUtil
from PostgreSQLUtil import PostgreSQLUtil
from OracleUtil import OracleUtil
import Conf


def getDatabase(p_dbtype, p_database=Conf.DATABASE):
    if p_dbtype == 'AsterixDB':
        db = AsterixDBUtil()
        return db
    elif p_dbtype == 'PostgreSQL':
        db = PostgreSQLUtil(p_database)
        return db
    elif p_dbtype == 'Oracle':
        db = OracleUtil(p_database)
        return db
    else:
        print 'Database: ', p_dbtype, ' is not supported now!'
        return

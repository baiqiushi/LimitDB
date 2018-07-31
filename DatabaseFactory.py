from MySQLUtil import MySQLUtil


def getDatabase(p_database):
    if p_database == 'MySQL':
        db = MySQLUtil()
        return db
    else:
        print 'Database: ', p_database, ' is not supported now!'
        return

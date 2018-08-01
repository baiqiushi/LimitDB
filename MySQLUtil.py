import mysql.connector
import os
import sys
import Conf
import time
from mysql.connector import DatabaseError


class MySQLUtil:
    def __init__(self):
        self.config = Conf.MYSQL_CONFIG
        self.conn = 0
        self.cursor = 0
        self.open()

    def open(self):
        self.conn = mysql.connector.connect(**self.config)
        self.cursor = self.conn.cursor()

    def query(self, sql):
        if not self.conn.is_connected():
            self.conn = mysql.connector.connect(**self.config)
            self.cursor = self.conn.cursor()
        print '[MySQLUtil]--> ', sql
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def close(self):
        self.cursor.close()
        self.conn.close()

    def commit(self):
        self.conn.commit()

    def GetCoordinate(self, tableName, keyword, limit):
        sql = "select x, y from limitdb." + tableName + " where match(text) against (\'+" + keyword + "\' in boolean mode)"
        if limit >= 0:
            sql += " limit " + str(limit)
        return self.query(sql)

    def GetID(self, tableName, keyword, limit):
        sql = "select id from limitdb." + tableName + " where match(text) against (\'+" + keyword + "\' in boolean mode)"
        if limit >= 0:
            sql += " limit " + str(limit)
        return self.query(sql)

    def queryLimit(self, tableName, keyword, limit):
        sql = "select x, y from limitdb." + tableName + " where match(text) against (\'+" + keyword + "\' in boolean mode)"
        if limit >= 0:
            sql += " limit " + str(limit)
        return self.query(sql)

    def queryLimitOrderBy(self, tableName, keyword, limit, orderBy):
        sql = "select x, y from limitdb." + tableName + " where match(text) against (\'+" + keyword + "\' in boolean mode)"
        if orderBy:
            sql += " order by " + orderBy
        if limit >= 0:
            sql += " limit " + str(limit)
        return self.query(sql)

    def restart(self):
        if sys.platform == 'darwin':
            os.system('sudo launchctl unload -F /Library/LaunchDaemons/com.oracle.oss.mysql.mysqld.plist')
            os.system('sudo launchctl load -F /Library/LaunchDaemons/com.oracle.oss.mysql.mysqld.plist')
        elif sys.platform == 'linux2':
            os.system('service mysqld restart')

        i = 0
        while i <= 10:
            try:
                self.open()
                break
            except DatabaseError:
                print 'wait 1s for db restarting ... ...'
                time.sleep(1)
                i += 1
        if i > 10:
            raise DatabaseError

    def queryDummy(self):
        dummy_sql = Conf.MYSQL_DUMMY_SQL
        return self.query(dummy_sql)

    def queryLimitWordInCountOrderBy(self, p_min_count, p_max_count, p_limit, p_orderBy):
        if p_orderBy == 'random':
            p_orderBy = 'RAND()'
        l_sql = 'SELECT word, count FROM limitdb.wordcount ' \
                ' WHERE count >= ' + str(p_min_count) + \
                '   and count < ' + str(p_max_count) + \
                ' ORDER BY ' + p_orderBy + \
                ' LIMIT ' + str(p_limit)
        return self.query(l_sql)

    def queryLimitWordNearCount(self, p_count, p_limit):
        l_sql = 'SELECT word, count FROM limitdb.wordcount ' \
                ' WHERE count >= ' + str(p_count / 2) + \
                '   and count < ' + str(p_count * 2) + \
                ' ORDER BY ABS(count - ' + str(p_count) + ') ' \
                ' LIMIT ' + str(p_limit)
        return self.query(l_sql)


def test():
    db = MySQLUtil()
    result = db.queryLimitWordInCountOrderBy(10000, 30000, 20, 'random')
    print result
    result = db.queryLimitWordNearCount(2000000, 2)
    print result

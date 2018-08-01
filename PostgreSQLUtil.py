import psycopg2
import os
import sys
import Conf
import time


class PostgreSQLUtil:
    def __init__(self):
        self.config = Conf.POSTGRESQL_CONFIG
        self.conn = 0
        self.cursor = 0
        self.open()

    def open(self):
        self.conn = psycopg2.connect(**self.config)
        self.cursor = self.conn.cursor()

    def query(self, sql):
        if self.conn is None:
            self.conn = psycopg2.connect(**self.config)
            self.cursor = self.conn.cursor()
        print '[PostgreSQLUtil]--> ', sql
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def close(self):
        self.cursor.close()
        self.conn.close()

    def commit(self):
        self.conn.commit()

    def GetCoordinate(self, tableName, keyword, limit):
        sql = "select x, y from " + tableName + \
              " where to_tsvector('english',text)@@to_tsquery('english','" + keyword + "')"
        if limit >= 0:
            sql += " limit " + str(limit)
        return self.query(sql)

    def GetID(self, tableName, keyword, limit):
        sql = "select id from " + tableName + \
              " where to_tsvector('english',text)@@to_tsquery('english','" + keyword + "')"
        if limit >= 0:
            sql += " limit " + str(limit)
        return self.query(sql)

    def queryLimit(self, tableName, keyword, limit):
        sql = "select x, y from " + tableName + \
              " where to_tsvector('english',text)@@to_tsquery('english','" + keyword + "')"
        if limit >= 0:
            sql += " limit " + str(limit)
        return self.query(sql)

    def queryLimitOrderBy(self, tableName, keyword, limit, orderBy):
        sql = "select x, y from " + tableName + \
              " where to_tsvector('english',text)@@to_tsquery('english','" + keyword + "')"
        if orderBy:
            sql += " order by " + orderBy
        if limit >= 0:
            sql += " limit " + str(limit)
        return self.query(sql)

    def restart(self):
        if sys.platform == 'darwin':
            os.system('brew services stop postgresql')
            os.system('brew services start postgresql')
        elif sys.platform == 'linux2':
            os.system('sudo systemctl restart postgresql')

        i = 0
        while i <= 10:
            try:
                self.open()
                break
            except psycopg2.DatabaseError:
                print 'wait 1s for db restarting ... ...'
                time.sleep(1)
                i += 1
        if i > 10:
            raise psycopg2.DatabaseError

    def queryDummy(self):
        dummy_sql = Conf.POSTGRESQL_DUMMY_SQL
        return self.query(dummy_sql)

    def queryLimitWordInCountOrderBy(self, p_min_count, p_max_count, p_limit, p_orderBy):
        if p_orderBy == 'random':
            p_orderBy = 'random()'
        l_sql = 'SELECT word, count FROM wordcount ' \
                ' WHERE count >= ' + str(p_min_count) + \
                '   and count < ' + str(p_max_count) + \
                ' ORDER BY ' + p_orderBy + \
                ' LIMIT ' + str(p_limit)
        return self.query(l_sql)

    def queryLimitWordNearCount(self, p_count, p_limit):
        l_sql = 'SELECT word, count FROM wordcount ' \
                ' WHERE count >= ' + str(p_count / 2) + \
                '   and count < ' + str(p_count * 2) + \
                ' ORDER BY ABS(count - ' + str(p_count) + ') ' \
                ' LIMIT ' + str(p_limit)
        return self.query(l_sql)


def test():
    db = PostgreSQLUtil()
    result = db.GetID('coord_tweets', 'job', 10)
    print result
    db.restart()
    result = db.queryDummy()
    print result
    result = db.GetCoordinate('coord_tweets', 'job', 10)
    print result
    result = db.queryLimitWordInCountOrderBy(10000, 30000, 20, 'random')
    print result
    result = db.queryLimitWordNearCount(2000000, 2)
    print result
    result = db.queryLimit('coord_tweets', 'job', 10)
    print result
    result = db.queryLimitOrderBy('coord_tweets', 'job', 10, 'x')
    print result


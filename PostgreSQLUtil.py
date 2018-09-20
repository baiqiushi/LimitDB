import psycopg2
import os
import sys
import Conf
import time
from random import choice
from string import ascii_lowercase


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

    def GetCoordinateRandomly(self, tableName, keyword, ratio):
        sql = "select x, y from " + tableName + \
              " where to_tsvector('english',text)@@to_tsquery('english','" + keyword + "')"
        if ratio >= 0:
            sql += " and random() <= " + str(ratio)
        return self.query(sql)

    def GetCoordinateHybrid(self, tableName, keyword, ratio, limit):
        sql = "select x, y from " + tableName + \
              " where to_tsvector('english',text)@@to_tsquery('english','" + keyword + "')"
        if ratio >= 0:
            sql += " and random() <= " + str(ratio)
        if limit >= 0:
            sql += " limit " + str(limit)
        return self.query(sql)

    def GetID(self, tableName, keyword, limit):
        sql = "select id from " + tableName + \
              " where to_tsvector('english',text)@@to_tsquery('english','" + keyword + "')"
        if limit >= 0:
            sql += " limit " + str(limit)
        return self.query(sql)

    def GetCount(self, tableName, keyword):
        sql = "select count(1) from " + tableName + \
              " where to_tsvector('english',text)@@to_tsquery('english','" + keyword + "')"
        results = self.query(sql)
        if len(results) < 1:
            return 0
        return results[0][0]

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

    def restart(self, version=9.6):
        if sys.platform == 'darwin':
            os.system('brew services stop postgresql')
            os.system('brew services start postgresql')
        elif sys.platform == 'linux2':
            if version >= 9.5:
                print 'sudo systemctl restart postgresql-' + str(version)
                os.system('sudo systemctl restart postgresql-' + str(version))
            else:
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
        # Generate a random 2 character string
        like_base = ''.join(choice(ascii_lowercase) for i in range(2))
        dummy_sql = Conf.POSTGRESQL_DUMMY_SQL_TEMP + '\'%' + like_base + '%\''
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

    def queryWordInCount(self, p_min_count, p_max_count):
        l_sql = 'SELECT word, count FROM wordcount ' \
                ' WHERE count >= ' + str(p_min_count) + \
                '   and count < ' + str(p_max_count) + \
                ' ORDER BY count DESC'
        return self.query(l_sql)

    def queryCurveInCount(self, p_min_count, p_max_count, p_tableName='wordcurve'):
        l_sql = 'SELECT word, count, q5, q10, q15, q20, ' \
                '       q25, q30, q35, q40, q45, q50, q55,' \
                '       q60, q65, q70, q75, q80, q85, q90, q95 ' \
                '  FROM ' + p_tableName + \
                ' WHERE count >= ' + str(p_min_count) + \
                '   and count <= ' + str(p_max_count) + \
                ' ORDER BY count DESC'
        results = self.query(l_sql)
        # convert the sub-tuples into lists
        results = map(lambda record: list(record), results)
        return results

    def queryLimitWordInCurveGroupOrderBy(self, p_group, p_limit, p_orderBy, p_tableName='wordcurve_grouped'):
        if p_orderBy == 'random':
            p_orderBy = 'random()'
        l_sql = 'SELECT word FROM ' + p_tableName + \
                ' WHERE kmeans = ' + str(p_group) + \
                ' ORDER BY ' + p_orderBy + \
                ' LIMIT ' + str(p_limit)
        results = self.query(l_sql)
        # convert the sub-tuples into single value
        results = map(lambda record: record[0], results)
        return results

    def queryKValuesInCount(self, p_min_count, p_max_count, p_tableName='wordkvalues'):
        l_sql = 'SELECT word, count, k70, k75, k80, k85, k90, k95' \
                '  FROM ' + p_tableName + \
                ' WHERE count >= ' + str(p_min_count) + \
                '   and count <= ' + str(p_max_count) + \
                ' ORDER BY count DESC'
        results = self.query(l_sql)
        # convert the sub-tuples into lists
        results = map(lambda record: list(record), results)
        return results


def test():
    db = PostgreSQLUtil()
    # result = db.GetID('coord_tweets', 'job', 10)
    # print result
    # db.restart()
    # result = db.queryDummy()
    # print result
    # result = db.GetCoordinate('coord_tweets', 'job', 10)
    # print result
    # result = db.queryLimitWordInCountOrderBy(10000, 30000, 20, 'random')
    # print result
    # result = db.queryLimitWordNearCount(2000000, 2)
    # print result
    # result = db.queryLimit('coord_tweets', 'job', 10)
    # print result
    # result = db.queryLimitOrderBy('coord_tweets', 'job', 10, 'x')
    # print result
    # result = db.queryCurveInCount(5000, 5020)
    # print result
    # result = db.queryLimitWordInCurveGroupOrderBy(0, 3, 'random')
    # print result
    result = db.GetCount('coord_tweets', 'work')
    print result


# test()

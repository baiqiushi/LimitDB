import psycopg2
import os
import sys
import Conf
import time
from random import choice
from string import ascii_lowercase


class PostgreSQLUtil:
    def __init__(self, p_database):
        self.config = Conf.POSTGRESQL_CONFIG
        self.config['database'] = p_database
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

    def command(self, sql):
        if self.conn is None:
            self.conn = psycopg2.connect(**self.config)
            self.cursor = self.conn.cursor()
        print '[PostgreSQLUtil]--> ', sql
        try:
            self.cursor.execute(sql)
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        return True

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

    def SumCoordinateHybrid(self, tableName, keyword, ratio, limit):
        sql = "select sum(x), sum(y) from " + tableName + \
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

    def queryWarmUp(self, tableName, keyword):
        sql = "select count(1) from " + tableName + \
              " where to_tsvector('english',text)@@to_tsquery('english','" + keyword + "')"
        return self.query(sql)

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

    # generate a sample of p_percentage for p_tableName
    # sample table name: 'p_tableName_p_mode_p_percentage', e.g. coord_tweets_bernoulli_1
    # return: sample table name, if successful, otherwise None
    def generateSample(self, p_tableName, p_percentage, p_mode='bernoulli'):
        l_sampleTableName = p_tableName + '_' + p_mode + '_' + p_percentage
        l_sql = 'create table if not exists ' + l_sampleTableName + \
                ' as select * from ' + p_tableName + \
                ' tablesample ' + p_mode + '(' + str(p_percentage) + ')'
        success = self.command(l_sql)
        if success:
            self.commit()
            return l_sampleTableName
        else:
            return None

    # build an inverted index on p_attribute for p_tableName
    # index name: 'idx_p_tableName_p_attribute'
    # return: index name, if successful, otherwise None
    def buildInvertedIndex(self, p_tableName, p_attribute):
        l_idxName = 'idx_' + p_tableName + '_' + p_attribute
        l_sql = 'CREATE INDEX if not exists ' + l_idxName + \
                ' ON ' + p_tableName + \
                ' USING GIN(to_tsvector(\'english\'::regconfig, ' + p_attribute + '))'
        success = self.command(l_sql)
        if success:
            self.commit()
            return l_idxName
        else:
            return None

    # load the csv file to the table
    def loadCSVToTable(self, p_file, p_tableName):
        l_sql = 'copy ' + p_tableName + ' from \'' + p_file + '\' DELIMITER \',\' CSV'
        success = self.command(l_sql)
        if success:
            self.commit()
            return True
        else:
            return False

    # insert list into the table
    def insertListToTable(self, p_list, p_tableName):
        l_sql = '''INSERT INTO ''' + p_tableName + ''' VALUES({})'''.format(','.join('%s' for x in p_list))
        print l_sql
        if self.conn is None:
            self.conn = psycopg2.connect(**self.config)
            self.cursor = self.conn.cursor()
        print '[PostgreSQLUtil]--> ', l_sql
        try:
            self.cursor.execute(l_sql, p_list)
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            return False
        self.commit()
        return True

    # query the curves of keywords in frequency range generated from p_table
    def queryCurves(self, p_table, p_min_freq, p_max_freq, p_quality_function='PH'):
        l_sql = 'SELECT cv.word, q5, q10, q15, q20, ' \
                '       q25, q30, q35, q40, q45, q50, q55,' \
                '       q60, q65, q70, q75, q80, q85, q90, q95 ' \
                '  FROM word_curves cv, word_counts cn' \
                ' WHERE cv.word = cn.word' \
                '   and cv.table_name = \'' + p_table + '\' ' + \
                '   and cv.quality_function = \'' + p_quality_function + '\' ' + \
                '   and cn.cardinality >= ' + str(p_min_freq) + \
                '   and cn.cardinality <= ' + str(p_max_freq) + \
                ' ORDER BY cn.cardinality DESC'
        results = self.query(l_sql)
        # convert the sub-tuples into lists
        results = map(lambda record: list(record), results)
        return results

    # query the curve of given keyword
    def queryCurve(self, p_table, p_quality_function, p_word):
        l_sql = 'SELECT q5, q10, q15, q20, ' \
                '       q25, q30, q35, q40, q45, q50, q55,' \
                '       q60, q65, q70, q75, q80, q85, q90, q95 ' \
                '  FROM word_curves ' \
                ' WHERE table_name = \'' + p_table + '\' ' + \
                '   and quality_function = \'' + p_quality_function + '\' ' + \
                '   and word = \'' + p_word + '\''
        results = self.query(l_sql)
        return results[0]

    # query the keywords in frequency range
    def queryKeywords(self, p_min_freq, p_max_freq):
        l_sql = 'SELECT word FROM word_counts ' \
                ' WHERE cardinality >= ' + str(p_min_freq) + \
                '   and cardinality < ' + str(p_max_freq) + \
                ' ORDER BY cardinality DESC'
        results = self.query(l_sql)
        # convert the sub-tuples into one element
        results = map(lambda record: record[0], results)
        return results

    def getDatabase(self):
        return self.config['database']


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
    # result = db.GetCount('coord_tweets', 'work')
    result = db.loadCSVToTable('/Users/white/1m_random_postgres.csv', 'dummy_table')
    print result


# test()

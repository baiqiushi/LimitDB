import os
import requests
import time

import Conf


class AsterixDBUtil:
    def __init__(self):
        self.host = Conf.ASTERIXDB_HOST
        self.url = 'http://' + self.host + ':19002/query/service'

    def open(self):
        pass

    def query(self, sql):
        print '[AsterixDBUtil]--> ', sql
        response = requests.post(self.url, data={'statement': sql})
        try:
            results = response.json()['results']
        except KeyError:
            results = []
        return results

    def close(self):
        pass

    def commit(self):
        pass

    def GetCoordinate(self, tableName, keyword, limit):
        sql = "select x, y from limitdb." + tableName + " where ftcontains(text, \'" + keyword + "\')"
        if limit >= 0:
            sql += " limit " + str(limit)
        # different from other DBs, results from AsterixDB are like this:
        # [{'y': 38.9907, 'x': -77.0261}, {'y': 42.324, 'x': -71.4537}, ...]
        results = self.query(sql)
        # transform the array of json objects into pure array
        results = map(lambda record: [record['x'], record['y']], results)
        return results

    def GetID(self, tableName, keyword, limit):
        sql = "select id from limitdb." + tableName + " where ftcontains(text, \'" + keyword + "\')"
        if limit >= 0:
            sql += " limit " + str(limit)
        # [{'id': 844218939236204548}, {'id': 844218979585470464}, ...]
        results = self.query(sql)
        # transform the array of json objects into pure array
        results = map(lambda record: record['id'], results)
        return results

    def GetCount(self, tableName, keyword):
        sql = "select count(*) as count from limitdb." + tableName + " where ftcontains(text, \'" + keyword + "\')"
        results = self.query(sql)
        # transform the array of json objects into pure array
        results = map(lambda record: record['count'], results)
        if len(results) < 1:
            return 0
        return results[0]

    def queryLimit(self, tableName, keyword, limit):
        sql = "select x, y from limitdb." + tableName + " where ftcontains(text, \'" + keyword + "\')"
        if limit >= 0:
            sql += " limit " + str(limit)
        # different from other DBs, results from AsterixDB are like this:
        # [{'y': 38.9907, 'x': -77.0261}, {'y': 42.324, 'x': -71.4537}, ...]
        results = self.query(sql)
        # transform the array of json objects into pure array
        results = map(lambda record: [record['x'], record['y']], results)
        return results

    def queryLimitOrderBy(self, tableName, keyword, limit, orderBy):
        sql = "select x, y from limitdb." + tableName + " where ftcontains(text, \'" + keyword + "\')"
        if orderBy:
            sql += " order by " + orderBy
        if limit >= 0:
            sql += " limit " + str(limit)
        # different from other DBs, results from AsterixDB are like this:
        # [{'y': 38.9907, 'x': -77.0261}, {'y': 42.324, 'x': -71.4537}, ...]
        results = self.query(sql)
        # transform the array of json objects into pure array
        results = map(lambda record: [record['x'], record['y']], results)
        return results

    @staticmethod
    def restart():
        print 'Stopping AsterixDB ... ...'
        start = time.time()
        os.system(Conf.ASTERIXDB_BIN + '/stop-sample-cluster.sh')
        end = time.time()
        print 'Stopping AsterixDB successfully, time =', end - start, 'seconds.'

        print 'Starting AsterixDB ... ...'
        start = time.time()
        os.system(Conf.ASTERIXDB_BIN + '/start-sample-cluster.sh')
        end = time.time()
        print 'Starting AsterixDB successfully, time =', end - start, 'seconds.'

    def queryDummy(self):
        dummy_sql = Conf.ASTERIXDB_DUMMY_SQL
        return self.query(dummy_sql)

    def queryLimitWordInCountOrderBy(self, p_min_count, p_max_count, p_limit, p_orderBy):
        if p_orderBy == 'random':
            p_orderBy = 'uuid()'
        l_sql = 'SELECT word, count FROM limitdb.wordcount ' \
                ' WHERE count >= ' + str(p_min_count) + \
                '   and count < ' + str(p_max_count) + \
                ' ORDER BY ' + p_orderBy + \
                ' LIMIT ' + str(p_limit)
        # different from other DBs, results from AsterixDB are like this:
        # [{u'count': 15534, u'word': u'advisor'}, ...]
        results = self.query(l_sql)
        # transform the array of json objects into pure array
        results = map(lambda record: [record['word'], record['count']], results)
        return results

    def queryLimitWordNearCount(self, p_count, p_limit):
        l_sql = 'SELECT word, count FROM limitdb.wordcount ' \
                ' WHERE count >= ' + str(p_count / 2) + \
                '   and count < ' + str(p_count * 2) + \
                ' ORDER BY abs(count - ' + str(p_count) + ') ' \
                ' LIMIT ' + str(p_limit)
        # different from other DBs, results from AsterixDB are like this:
        # [{u'count': 15534, u'word': u'advisor'}, ...]
        results = self.query(l_sql)
        # transform the array of json objects into pure array
        results = map(lambda record: [record['word'], record['count']], results)
        return results

    def queryWordInCount(self, p_min_count, p_max_count):
        l_sql = 'SELECT word, count FROM limitdb.wordcount ' \
                ' WHERE count >= ' + str(p_min_count) + \
                '   and count < ' + str(p_max_count) + \
                ' ORDER BY count DESC'
        # different from other DBs, results from AsterixDB are like this:
        # [{u'count': 15534, u'word': u'advisor'}, ...]
        results = self.query(l_sql)
        # transform the array of json objects into pure array
        results = map(lambda record: [record['word'], record['count']], results)
        return results

    def queryCurveInCount(self, p_min_count, p_max_count):
        l_sql = 'SELECT word, count, q5, q10, q15, q20, ' \
                '       q25, q30, q35, q40, q45, q50, q55,' \
                '       q60, q65, q70, q75, q80, q85, q90, q95 ' \
                '  FROM limitdb.wordcurve ' \
                ' WHERE count >= ' + str(p_min_count) + \
                '   and count <= ' + str(p_max_count) + \
                ' ORDER BY count DESC'
        # different from other DBs, results from AsterixDB are like this:
        # [{u'count': 15534, u'word': u'advisor', u'q5': 0.031, ...}, ...]
        results = self.query(l_sql)
        # transform the array of json objects into pure array
        results = map(lambda record: [record['word'], record['count'], record['q5'], record['q10'], record['q15'],
                                      record['q20'], record['q25'], record['q30'], record['q35'], record['q40'],
                                      record['q45'], record['q50'], record['q55'], record['q60'], record['q65'],
                                      record['q70'], record['q75'], record['q80'], record['q85'], record['q90'],
                                      record['q95']], results)
        return results

    def queryAnalyzedCurveInCount(self, p_min_count, p_max_count):
        l_sql = 'SELECT word, count, q5, q10, q15, q20, ' \
                '       q25, q30, q35, q40, q45, q50, q55,' \
                '       q60, q65, q70, q75, q80, q85, q90, q95, ' \
                '       len, mean, std, var' \
                '  FROM limitdb.wordcurve_analyzed ' \
                ' WHERE count >= ' + str(p_min_count) + \
                '   and count <= ' + str(p_max_count) + \
                ' ORDER BY count DESC'
        # different from other DBs, results from AsterixDB are like this:
        # [{u'count': 15534, u'word': u'advisor', u'q5': 0.031, ...}, ...]
        results = self.query(l_sql)
        # transform the array of json objects into pure array
        results = map(lambda record: [record['word'], record['count'], record['q5'], record['q10'], record['q15'],
                                      record['q20'], record['q25'], record['q30'], record['q35'], record['q40'],
                                      record['q45'], record['q50'], record['q55'], record['q60'], record['q65'],
                                      record['q70'], record['q75'], record['q80'], record['q85'], record['q90'],
                                      record['q95'], record['len'], record['mean'], record['std'], record['var']],
                      results)
        return results

    def queryLimitWordInCurveGroupOrderBy(self, p_group, p_limit, p_orderBy):
        if p_orderBy == 'random':
            p_orderBy = 'random()'
        l_sql = 'SELECT word FROM limitdb.wordcurve_grouped ' \
                ' WHERE kmeans = ' + str(p_group) + \
                ' ORDER BY ' + p_orderBy + \
                ' LIMIT ' + str(p_limit)
        # different from other DBs, results from AsterixDB are like this:
        # [{u'count': 15534, u'word': u'advisor'}, ...]
        results = self.query(l_sql)
        # transform the array of json objects into pure array
        results = map(lambda record: record['word'], results)
        return results


def test():
    db = AsterixDBUtil()
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


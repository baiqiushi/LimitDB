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
        return response.json()['results']

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


def test():
    db = AsterixDBUtil()
    result = db.GetID('coord_tweets', 'job', 10)
    print result
    result = db.GetID('coord_tweets', 'job', 10)
    print result
    result = db.queryLimitWordInCountOrderBy(10000, 30000, 20, 'random')
    print result
    result = db.queryLimitWordNearCount(2000000, 2)
    print result

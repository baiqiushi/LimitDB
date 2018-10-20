import cx_Oracle
import os
import sys
import Conf
import time


class OracleUtil:
    def __init__(self, p_database):
        self.config = Conf.ORACLE_CONFIG
        self.config['database'] = p_database
        self.conn = 0
        self.cursor = 0
        self.open()

    def open(self):
        self.conn = cx_Oracle.connect(self.config['connectStr'])
        self.cursor = self.conn.cursor()

    def query(self, sql):
        if self.conn is None:
            self.conn = cx_Oracle.connect(self.config['connectStr'])
            self.cursor = self.conn.cursor()
        print ('[OracleUtil]--> ', sql)
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def command(self, sql):
        if self.conn is None:
            self.conn = cx_Oracle.connect(self.config['connectStr'])
            self.cursor = self.conn.cursor()
        print ('[OracleUtil]--> ', sql)
        try:
            self.cursor.execute(sql)
        except (Exception, cx_Oracle.DatabaseError) as error:
            print(error)
        return True

    def close(self):
        self.cursor.close()
        self.conn.close()

    def commit(self):
        self.conn.commit()

    def GetCoordinate(self, tableName, keyword, limit):
        sql = "select x, y from " + tableName + \
              " where contains(text, '" + keyword + "') > 0"
        if limit >= 0:
            sql += " and rownum <= " + str(limit)
        return self.query(sql)

    def GetID(self, tableName, keyword, limit):
        sql = "select id from " + tableName + \
              " where contains(text, '" + keyword + "') > 0"
        if limit >= 0:
            sql += " and rownum <= " + str(limit)
        return self.query(sql)

    def GetCount(self, tableName, keyword):
        sql = "select count(1) from " + tableName + \
              " where contains(text, '" + keyword + "') > 0"
        results = self.query(sql)
        if len(results) < 1:
            return 0
        return results[0][0]

    def queryLimit(self, tableName, keyword, limit):
        sql = "select x, y from " + tableName + \
              " where contains(text, '" + keyword + "') > 0"
        if limit >= 0:
            sql += " and rownum <= " + str(limit)
        return self.query(sql)

    def restart(self, version=9.6):
        if sys.platform == 'darwin':
            os.system('brew services stop postgresql')
            os.system('brew services start postgresql')
        elif sys.platform == 'linux2':
            if version >= 9.5:
                print ('sudo systemctl restart postgresql-' + str(version))
                os.system('sudo systemctl restart postgresql-' + str(version))
            else:
                os.system('sudo systemctl restart postgresql')

        i = 0
        while i <= 10:
            try:
                self.open()
                break
            except cx_Oracle.DatabaseError:
                print ('wait 1s for db restarting ... ...')
                time.sleep(1)
                i += 1
        if i > 10:
            raise cx_Oracle.DatabaseError

    def queryDummy(self):
        return None

    def queryWarmUp(self, tableName, keyword):
        sql = "select count(1) from " + tableName + \
              " where contains(text, '" + keyword + "') > 0"
        return self.query(sql)

    # load the csv file to the table
    def loadCSVToTable(self, p_file, p_tableName):
        success = True
        if success:
            self.commit()
            return True
        else:
            return False

    # insert list into the table
    def insertListToTable(self, p_list, p_tableName):
        l_sql = '''INSERT INTO ''' + p_tableName + ''' VALUES({})'''.format(','.join('%s' for x in p_list))
        print (l_sql)
        if self.conn is None:
            self.conn = cx_Oracle.connect(self.config['connectStr'])
            self.cursor = self.conn.cursor()
        print ('[OracleUtil]--> ', l_sql)
        try:
            self.cursor.execute(l_sql, p_list)
        except (Exception, cx_Oracle.DatabaseError) as error:
            print(error)
            return False
        self.commit()
        return True

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

    def getDatabase(self):
        return self.config['database']


def test():
    db = OracleUtil('limitdb')
    result = db.GetID('coord_tweets', 'job', 10)
    print (result)


# test()

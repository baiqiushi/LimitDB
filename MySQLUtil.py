import mysql.connector
import os
import sys

import time
from mysql.connector import DatabaseError


class MySQLUtil:
    def __init__(self):
        self.config = {
          'user': 'root',
          'password': '3979',
          'host': 'localhost',
          'database': 'limitdb',
          'raise_on_warnings': True,
          'use_pure': False,
        }
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


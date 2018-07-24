import mysql.connector

config = {
  'user': 'root',
  'password': '3979',
  'host': 'localhost',
  'database': 'limitdb',
  'raise_on_warnings': True,
  'use_pure': False,
}

conn = mysql.connector.connect(**config)
cursor = conn.cursor()


def query(sql):
    cursor.execute(sql)
    return cursor.fetchall()


def close():
    cursor.close()
    conn.close()


def GetCoordinate(tableName, keyword, limit):
    sql = "select x, y from limitdb." + tableName + " where match(text) against (\'+" + keyword + "\' in boolean mode)"
    if limit >= 0:
        sql += " limit " + str(limit)
    return query(sql)


def queryLimit(tableName, keyword, limit):
    sql = "select x, y from limitdb." + tableName + " where match(text) against (\'+" + keyword + "\' in boolean mode)"
    if limit >= 0:
        sql += " limit " + str(limit)
    return query(sql)


def queryLimitOrderBy(tableName, keyword, limit, orderBy):
    sql = "select x, y from limitdb." + tableName + " where match(text) against (\'+" + keyword + "\' in boolean mode)"
    if not orderBy:
        sql += " order by " + orderBy
    if limit >= 0:
        sql += " limit " + str(limit)
    return query(sql)

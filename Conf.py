# ===========================
#         Constants
# ===========================

# Common config
# Options: MySQL AsterixDB PostgreSQL
DBTYPE = 'PostgreSQL'
DATABASE = 'limitdb2'
TABLE = 'coord_tweets'
ORDER_BY = 'id'

# AsterixDB config
ASTERIXDB_BIN = '/Users/white/asterixdb/opt/local/bin'
ASTERIXDB_HOST = 'localhost'
ASTERIXDB_DUMMY_SQL = 'select count(1) from ' \
                      '(select t.text from limitdb.dummy_table t where t.id < 865350497200371700) p ' \
                        'where p.text like \'%lo%\' '

# MySQL config
MYSQL_CONFIG = {
  'user': 'root',
  'password': 'Root3979!',
  'host': 'localhost',
  'database': DATABASE,
  'raise_on_warnings': True,
  'use_pure': False,
}

MYSQL_DUMMY_SQL = 'select count(1) from (select t.text from limitdb.dummy_table t where t.id < 865350497200371700) p ' \
            'where p.text like \'%lo%\' '

# PostgreSQL config
POSTGRESQL_CONFIG = {
    'host': 'localhost',
    'user': 'postgres',
    'password': 'postgres',
    'database': DATABASE
}

# For 10 M data set
# POSTGRESQL_DUMMY_SQL = 'Select count(1) from ' \
#                        '(select t.text from dummy_table t where t.id < 865350497200371700) p ' \
#                        'where p.text like \'%lo%\' '

# POSTGRESQL_DUMMY_SQL = 'select * from dummy_table'

# For 200 M data set
POSTGRESQL_DUMMY_SQL = 'Select count(1) from ' \
                       '(select t.text from dummy_table t where t.id < 799999999999999999) p ' \
                       'where p.text like \'%lo%\' '


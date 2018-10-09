# ===========================
#         Constants
# ===========================

# Common config
# Options: MySQL AsterixDB PostgreSQL
DBTYPE = 'PostgreSQL'
DATABASE = 'limitdb'
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

POSTGRESQL_RANDOM_DATA_FILE = '/home/waans11/limit/200m_random_postgres.csv'

POSTGRESQL_TABLE_COMMANDS = [
    # create random table
    {'key': 'create_random_table',
     'cmd': """
            CREATE TABLE IF NOT EXISTS coord_tweets
            (
              id bigint NOT NULL,
              text text,
              x float,
              y float,
              CONSTRAINT coord_tweets_pk PRIMARY KEY (id)
            )
            WITH (
              OIDS=FALSE
            )
            """,
     'comment': 'create random table'
     },
    # load data into random table
    {'key': 'load_random_table',
     'cmd': 'COPY coord_tweets FROM \'' + POSTGRESQL_RANDOM_DATA_FILE + '\' DELIMITER \',\' CSV',
     'comment': 'load data into random table'
     },
    # create index for random table
    {'key': 'index_random_table',
     'cmd': """
            CREATE INDEX IF NOT EXISTS idx_ct_txt
                ON coord_tweets
                USING GIN
                (to_tsvector('english'::regconfig, text))
            """,
     'comment': 'create index for random table'
     },
    # create biased table and insert data
    {'key': 'create_biased_table',
     'cmd': 'CREATE TABLE IF NOT EXISTS coord_tweets_sorted AS SELECT * FROM coord_tweets ORDER BY x, y',
     'comment': 'create biased table and insert data'
     },
    # create index for biased table
    {'key': 'index_biased_table',
     'cmd': """
            CREATE INDEX IF NOT EXISTS idx_ctsd_txt
              ON coord_tweets_sorted
              USING GIN
              (to_tsvector('english'::regconfig, text))
            """,
     'comment': 'create index for biased table'
     },
    # create dummy table and insert data
    {'key': 'create_dummy_table',
     'cmd': 'CREATE TABLE IF NOT EXISTS dummy_table AS SELECT * FROM coord_tweets',
     'comment': 'create dummy table and insert data'
     },
    # create word_counts table
    {'key': 'create_word_counts',
     'cmd': """
            CREATE TABLE IF NOT EXISTS word_counts
            (
              word text,
              frequency integer,
              cardinality integer
            )
            WITH (
              OIDS=FALSE
            )
            """,
     'comment': 'create word_counts table'
     },
    # get word_counts data
    {'key': 'load_word_counts',
     'cmd': 'INSERT INTO word_counts '
            'SELECT word, nentry, ndoc '
            'FROM ts_stat(\'SELECT to_tsvector(\'\'english\'\'::regconfig, text) FROM coord_tweets\')',
     'comment': 'get word_counts data'
     },
    # clean word_counts data
    {'key': 'clean_word_counts',
     'cmd': """
            DELETE FROM word_counts where char_length(word) < 3 or word !~* '^[a-z]*$ or frequency < 1000'
            """,
     'comment': 'clean word_counts data'
     },
    # create word_curves table
    {'key': 'create_word_curves',
     'cmd': """
            CREATE TABLE IF NOT EXISTS word_curves
            (
                table_name text,
                quality_function varchar(5),
                word text,
                q5 float,
                q10 float,
                q15 float,
                q20 float,
                q25 float,
                q30 float,
                q35 float,
                q40 float,
                q45 float,
                q50 float,
                q55 float,
                q60 float,
                q65 float,
                q70 float,
                q75 float,
                q80 float,
                q85 float,
                q90 float,
                q95 float,
                query_time float,
                curve_time float,
                CONSTRAINT word_curves_pk PRIMARY KEY (table_name, quality_function, word)
            )
            WITH (
              OIDS=FALSE
            )
            """,
     'comment': 'create word_curves table'
     },
    # create word_clusters table
    {'key': 'create_word_clusters',
     'cmd': """
            CREATE TABLE IF NOT EXISTS word_clusters
            (
                table_name text,
                min_freq integer,
                max_freq integer,
                k_means_k integer,
                word text,
                cluster_label integer
            )
            WITH (
              OIDS=FALSE
            )
            """,
     'comment': 'create word_clusters table'
     }
]

# For 10 M data set
# POSTGRESQL_DUMMY_SQL = 'Select count(1) from ' \
#                        '(select t.text from dummy_table t where t.id < 865350497200371700) p ' \
#                        'where p.text like \'%lo%\' '

# POSTGRESQL_DUMMY_SQL = 'select * from dummy_table'

# For 200 M data set
POSTGRESQL_DUMMY_SQL = 'Select count(1) from ' \
                       '(select t.text from dummy_table t where t.id < 799999999999999999) p ' \
                       'where p.text like \'%lo%\' '

POSTGRESQL_DUMMY_SQL_TEMP = 'Select count(1) from ' \
                            '(select t.text from dummy_table t where t.id < 799999999999999999) p ' \
                            'where p.text like '

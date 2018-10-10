import argparse
import time
from random import shuffle
import Conf
import DatabaseFactory

###########################################################
#   prepareDB
#
# -d / -dbtype     database product:
#                  [MySQL, PostgreSQL, AsterixDB]
# -f / -file       random data file:
#                  default: /home/waans11/limit/200m_random_postgres.csv
###########################################################

# 1. Parse arguments
parser = argparse.ArgumentParser(description='Prepare Database by creating tables needed for later experiments.')
parser.add_argument('-d', '--dbtype', help='dbtype: target database product',
                    choices=['PostgreSQL', 'MySQL', 'AsterixDB'], default='PostgreSQL', required=False)
parser.add_argument('-b', '--database', help='database: target database connect to', required=False)
parser.add_argument('-f', '--file', help='file: absolute path to csv file for random table', required=False)
parser.add_argument('-c', '--cmd', nargs='+', help='cmd: commands that you want to run or all of them [all]',
                    choices=['create_random_table', 'load_random_table', 'index_random_table', 'create_biased_table',
                             'index_biased_table', 'create_dummy_table', 'create_word_counts', 'load_word_counts',
                             'clean_word_counts', 'create_word_curves', 'create_word_clusters', 'create_combined_table',
                             'all'], required=True)
args = parser.parse_args()

dbtype = args.dbtype
database = args.database
if database is None:
    database = Conf.DATABASE
randomDataFile = Conf.POSTGRESQL_RANDOM_DATA_FILE
commands = args.cmd

if args.file is not None:
    randomDataFile = args.file

# 2. Run scripts
print '================================================='
print '    LimitDB - prepare Database'
print '================================================='
print 'dbtype:', dbtype
print 'database:', database
print 'random data file:', randomDataFile
print 'command:', commands
print '================================================='
print '-----------------> Start! <-------------------'
print ''

db = DatabaseFactory.getDatabase(dbtype, database)

preparationCommands = []
if dbtype == 'PostgreSQL':
    preparationCommands = Conf.POSTGRESQL_TABLE_COMMANDS


def getPreparationCommand(p_key, p_preparationCommands):
    for l_command in p_preparationCommands:
        if l_command['key'] == p_key:
            return l_command
    return None


t0 = time.time()
# if command is 'all', run all commands sequentially
if len(commands) == 1 and commands[0] == 'all':
    for command in preparationCommands:
        print command['comment']
        t1 = time.time()
        success = db.command(command['cmd'])
        if success:
            db.commit()
            print '------------------->  Success! [o]'
        else:
            print '------------------->  Failed!  [x]'
        t2 = time.time()
        print '[Time] Operation:', t2 - t1, ',  Totally:', t2 - t0
# otherwise, run commands listed by the user
else:
    for commandKey in commands:
        preparationCommand = getPreparationCommand(commandKey, preparationCommands)
        if preparationCommand is not None:
            print preparationCommand['comment']
            t1 = time.time()
            success = db.command(preparationCommand['cmd'])
            if success:
                db.commit()
                print '------------------->  Success! [o]'
            else:
                print '------------------->  Failed!  [x]'
            t2 = time.time()
            print '[Time] Operation:', t2 - t1, ',  Totally:', t2 - t0

# create_combined_table is a special case
if len(commands) == 1 and commands[0] == 'create_combined_table':
    # 1. create the combined table
    l_sql = """CREATE TABLE IF NOT EXISTS coord_tweets_combined
                (
                  id bigint NOT NULL,
                  text text,
                  x float,
                  y float,
                  CONSTRAINT coord_tweets_combined_pk PRIMARY KEY (id)
                )
                WITH (
                  OIDS=FALSE
                )
            """
    success = db.command(l_sql)
    if success:
        db.commit()
        print '------------------->  Success! [o]'
    else:
        print '------------------->  Failed!  [x]'

    # 2. fetch the max(x), min(x), max(y), min(y) from coord_tweets
    l_sql = 'select max(x), min(x), max(y), min(y) from coord_tweets'
    results = db.query(l_sql)
    # get rid of wrapping list
    results = results[0]
    max_x = results[0] + 1
    min_x = results[1]
    max_y = results[2] + 1
    min_y = results[3]
    print 'max(x):', max_x
    print 'min(x):', min_x
    print 'max(y):', max_y
    print 'min(y):', min_y
    x_step = (max_x - min_x) / 10.0
    y_step = (max_y - min_y) / 10.0
    steps = []
    for i in range(0, 10, 1):
        for j in range(0, 10, 1):
            steps.append([i, j])
    print 'steps:', steps
    shuffle(steps)
    print 'shuffled steps:', steps
    for step in steps:
        dx = step[0]
        dy = step[1]
        l_sql = "insert into coord_tweets_combined " \
                "select id, text, x, y from coord_tweets " \
                " where x >= {} " \
                "   and x < {} " \
                "   and y >= {} " \
                "   and y < {}".format(min_x + x_step * dx, min_x + x_step * (dx + 1),
                                       min_y + y_step * dy, min_y + y_step * (dy + 1))
        success = db.command(l_sql)
        if success:
            print '------------------->  Success! [o]'
        else:
            print '------------------->  Failed!  [x]'
    db.commit()


db.close()
print '===================> End! <==================='
print 'LimitDB - prepare Database'
print 'dbtype:', dbtype
print 'database:', database
print 'random data file:', randomDataFile
print 'Total time:', time.time() - t0
print '================================================='

import argparse
import time

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
parser.add_argument('-c', '--cmd', help='cmd: command that you want to run or all of them [all]',
                    choices=['create_random_table', 'load_random_table', 'index_random_table', 'create_biased_table',
                             'index_biased_table', 'create_dummy_table', 'create_word_counts', 'load_word_counts',
                             'clean_word_counts', 'create_word_curves', 'create_word_clusters', 'all'], required=True)
args = parser.parse_args()

dbtype = args.dbtype
database = args.database
if database is None:
    database = Conf.DATABASE
randomDataFile = Conf.POSTGRESQL_RANDOM_DATA_FILE
cmd = args.cmd

if args.file is not None:
    randomDataFile = args.file

# 2. Run scripts
print '================================================='
print '    LimitDB - prepare Database'
print '================================================='
print 'dbtype:', dbtype
print 'database:', database
print 'random data file:', randomDataFile
print 'command:', cmd
print '================================================='
print '-----------------> Start! <-------------------'
print ''

db = DatabaseFactory.getDatabase(dbtype, database)

preparationCommands = []
if dbtype == 'PostgreSQL':
    preparationCommands = Conf.POSTGRESQL_TABLE_COMMANDS

t0 = time.time()
for command in preparationCommands:
    if command['key'] == cmd or cmd == 'all':
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

print '===================> End! <==================='
print 'LimitDB - prepare Database'
print 'dbtype:', dbtype
print 'database:', database
print 'random data file:', randomDataFile
print 'Total time:', time.time() - t0
print '================================================='

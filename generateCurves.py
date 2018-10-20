import argparse
import KeywordsUtil
import DatabaseFactory
import CurveGenerator
import time
import Conf

###########################################################
#   generateCurves
#
# -d / -dbtype     database product:
#                  [MySQL, PostgreSQL, AsterixDB]
# -t / -table      target table name
# -k / -keywords   list of keywords we choose
# -f1 / -min_freq  min frequency of the keywords we choose
# -f2 / -max_freq  max frequency of the keywords we choose
#
###########################################################

# 1. Parse arguments
parser = argparse.ArgumentParser(description='Generate curves for given keywords '
                                             'within list or in given frequency range.')
parser.add_argument('-d', '--dbtype', help='target database type',
                    choices=['PostgreSQL', 'AsterixDB', 'Oracle'], default='PostgreSQL', required=False)
parser.add_argument('-b', '--database', help='database: target database connect to', required=False)
parser.add_argument('-t', '--table', help='table: target table name', required=True)
parser.add_argument('-f1', '--min_freq', help='min_freq: min frequency of the keywords we choose', required=False)
parser.add_argument('-f2', '--max_freq', help='max_freq: max frequency of the keywords we choose', required=False)
parser.add_argument('-k', '--keywords', nargs='+', help='keywords: list of keywords we choose', required=False)
parser.add_argument('-q', '--q_function', help='q_function: quality function used to generate curves', required=False,
                    choices=['PH', 'EMD', 'MSE'], default='PH')
args = parser.parse_args()

dbtype = args.dbtype
database = args.database
if database is None:
    database = Conf.DATABASE
tableName = args.table
min_freq = args.min_freq
max_freq = args.max_freq
keywords = args.keywords
quality_function = args.q_function

scale = [1, 1]
csvBasePath = '.'

byFrequency = False
byGivenKeywords = False
if min_freq is not None and max_freq is not None:
    byFrequency = True
    if keywords is not None:
        print 'by frequency or by keywords list can not be used at the same time'
        exit(-1)
else:
    if keywords is not None:
        byGivenKeywords = True
    else:
        print '-f1/-min-freq and -f2/-max-freq need to be given or -k/-keywords need to be given'
        exit(-1)


db = DatabaseFactory.getDatabase(dbtype, database)

if byFrequency:
    keywords = KeywordsUtil.pickInFrequencyRange(db, min_freq, max_freq)

# 2. Run scripts
print '================================================='
print '    LimitDB - generate Curves'
print '================================================='
print 'dbtype:', dbtype
print 'database', database
print 'target table:', tableName
print 'keywords frequency:', '[' + str(min_freq) + ', ' + str(max_freq) + ']'
print 'keywords list:', keywords
print 'scale:', scale
print 'quality function:', quality_function
print '================================================='
print '-----------------> Start! <-------------------'
print ''

t0 = time.time()
curves = CurveGenerator.generateCurves(db, tableName, keywords, scale, quality_function)
t1 = time.time()
print '[Time] Curve generation:', t1 - t0

# write curves to csv file
csvFile = CurveGenerator.writeCurvesToCSV(tableName, curves, csvBasePath)
print 'Append the curves to csv file:', csvFile
# insert curves into database table 'word_curves'
print 'Insert the curves into database table "word_curves":', CurveGenerator.insertCurvesToDB(db, curves)

print '===================> End! <==================='
print 'LimitDB - generate Curves'
print '================================================='
print 'dbtype:', dbtype
print 'database:', database
print 'target table:', tableName
print 'keywords frequency:', '[' + str(min_freq) + ', ' + str(max_freq) + ']'
print 'keywords list:', keywords
print 'scale:', scale
print 'quality function:', quality_function
print 'Total time:', time.time() - t0
print '================================================='

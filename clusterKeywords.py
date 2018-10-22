import argparse
import time
import DatabaseFactory
import CurveGenerator
import KeywordsClusterer
import KeywordsUtil
import math
import Conf

###########################################################
#   clusterKeywords
#
# -d / -dbtype     database product:
#                  [MySQL, PostgreSQL, AsterixDB]
# -t / -table      target table name
# -p / -percentage sample percentage [1~100]
# -m / -mode       sample mode, default: bernoulli
# -a / -attribute  text attribute name: text
# -f1 / -min_freq  min frequency of the keywords we choose
# -f2 / -max_freq  max frequency of the keywords we choose
#
###########################################################

# 1. Parse arguments
parser = argparse.ArgumentParser(description='Cluster keywords for given frequency range '
                                             'by sampling given percentage on given target table.')
parser.add_argument('-d', '--dbtype', help='target database type',
                    choices=['PostgreSQL', 'MySQL', 'AsterixDB'], default='PostgreSQL', required=False)
parser.add_argument('-b', '--database', help='database: target database connect to', required=False)
parser.add_argument('-t', '--table', help='table: target table name', required=True)
parser.add_argument('-p', '--percentage', help='percentage: sampling ratio for clustering', required=True)
parser.add_argument('-m', '--mode', help='mode: sampling mode for clustering, default: bernoulli', required=False,
                    default='bernoulli')
parser.add_argument('-a', '--attribute', help='attribute: text attribute for building index on, default: text',
                    required=False, default='text')
parser.add_argument('-f1', '--min_freq', help='min_freq: min frequency of the keywords we choose', required=True)
parser.add_argument('-f2', '--max_freq', help='max_freq: max frequency of the keywords we choose', required=True)
parser.add_argument('-k', '--kmeans', help='kmeans: # of groups for k-means algorithm', required=False,
                    default=10)
parser.add_argument('-ce', '--curve_exists', help='curve_exists: ? if YES/yes/Y/y, then skip the curves generation phase.',
                    required=False, default='no')
args = parser.parse_args()

dbtype = args.dbtype
database = args.database
if database is None:
    database = Conf.DATABASE
tableName = args.table
sample_percentage = args.percentage
sample_mode = args.mode
text_attr = args.attribute
min_freq = args.min_freq
max_freq = args.max_freq
k = int(args.kmeans)
curve_exists = args.curve_exists
# calculate the scale factors according to sample percentage
scale_factor = math.floor(100 / int(sample_percentage))
scale_x = math.floor(math.sqrt(scale_factor))
scale_y = math.floor(math.sqrt(scale_factor))
scale = [scale_x, scale_y]

csvBasePath = '.'

# 2. Run scripts
print '================================================='
print '    LimitDB - cluster keywords'
print '================================================='
print 'dbtype:', dbtype
print 'database', database
print 'target table:', tableName
print 'sample percentage:', str(sample_percentage) + '%'
print 'sample mode:', sample_mode
print 'text attribute:', text_attr
print 'keywords frequency:', '[' + str(min_freq) + ', ' + str(max_freq) + ']'
print 'k-means k:', k
print 'scale:', scale
print '================================================='
print '-----------------> Start! <-------------------'
print ''

db = DatabaseFactory.getDatabase(dbtype, database)

times = {}

# 3. (1) Generate random sample of target table
t0 = time.time()
sample_table = db.generateSample(tableName, sample_percentage, sample_mode)
t1 = time.time()
times['sample'] = t1 - t0
print '[Time] Sample generation:', t1 - t0, ',  Totally:', time.time() - t0
if sample_table is None:
    print 'Generate random sample failed! Exit'
    exit(-1)

# 3. (2) Build inverted index for sample table
t2 = time.time()
sample_index = db.buildInvertedIndex(sample_table, text_attr)
t3 = time.time()
times['index'] = t3 - t2
print '[Time] Index building:', t3 - t2, ', Totally:', time.time() - t0
if sample_index is None:
    print 'Build inverted index for sample table failed! Exit'
    exit(-1)

# 3. (3) Pick keywords within given frequency range
keywords = KeywordsUtil.pickInFrequencyRange(db, min_freq, max_freq)
print 'Keywords handled:', keywords

# 3. (4) Generate Curves on sample table
if curve_exists != 'YES' and curve_exists != 'yes' and curve_exists != 'Y' and curve_exists != 'y':
    t4 = time.time()
    sample_curves = CurveGenerator.generateCurves(db, sample_table, keywords, scale)
    t5 = time.time()
    times['curve'] = t5 - t4
    print '[Time] Curves generation:', t5 - t4, ', Totally:', time.time() - t0
    # write curves to csv file
    csvFile = CurveGenerator.writeCurvesToCSV(sample_table, sample_curves, csvBasePath)
    print 'Write the curves to csv file:', csvFile
    # insert curves into database table 'word_curves'
    print 'Insert the curves into database table "word_curves":', CurveGenerator.insertCurvesToDB(db, sample_curves)
    # load curves into database table 'word_curves'
    # print 'Load the curves into database table "word_curves":', CurveGenerator.loadCurvesCSVToDB(db, csvFile)


# 3. (5) Cluster the curves of keywords
t6 = time.time()
labeled_curves = KeywordsClusterer.clusterByCurves(db, sample_table, min_freq, max_freq, k)
t7 = time.time()
times['cluster'] = t7 - t6
print '[Time] Curves clustering:', t7 - t6, ', Totally:', time.time() - t0
# write labeled keywords to csv file
csvFile = KeywordsClusterer.writeLabeledKeywordsToCSV(sample_table, min_freq, max_freq, labeled_curves, csvBasePath, k)
print 'Write the labeled keywords to csv file:', csvFile
# insert labeled keywords into database table 'word_clusters'
print 'insert the labeled keywords into database table "word_clusters":', KeywordsClusterer.insertClustersCSVToDB(db, csvFile)
# load labeled keywords into database table 'word_clusters'
# print 'Load the labeled keywords into database table "word_clusters":', KeywordsClusterer.loadClustersCSVToDB(db, csvFile)

print '----------------------------------------------'
print times.keys()
print times.values()
print 'total clustering time:', sum(times.values())
print '===================> End! <==================='
print 'LimitDB - cluster keywords'
print '================================================='
print 'dbtype:', dbtype
print 'database', database
print 'target table:', tableName
print 'sample percentage:', str(sample_percentage) + '%'
print 'sample mode:', sample_mode
print 'text attribute:', text_attr
print 'keywords frequency:', '[' + str(min_freq) + ', ' + str(max_freq) + ']'
print 'k-means k:', k
print 'scale:', scale
print 'Total time:', time.time() - t0
print '================================================='

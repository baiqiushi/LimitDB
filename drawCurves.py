import argparse
import DatabaseFactory
import PlotUtil

###########################################################
#   drawCurves
#
# -d / -dbtype     database product:
#                  [MySQL, PostgreSQL, AsterixDB]
#
###########################################################

# 1. Parse arguments
parser = argparse.ArgumentParser(description='Generate curves for given keywords '
                                             'within list or in given frequency range.')
parser.add_argument('-d', '--dbtype', help='target database type',
                    choices=['PostgreSQL', 'MySQL', 'AsterixDB'], default='PostgreSQL', required=False)
args = parser.parse_args()

dbtype = args.dbtype

pdfBasePath = '.'
fileName = 'curves-on-datasize'
labels = ['10M', '100M', '200M']
# x axis is the same as k_percentages
x = range(5, 100, 5)
# Same keyword - soccer
# Same dataset - random
# Same q_funct - PH
# Diff datasize - 10M, 100M, 200M
targetCurves = [
    {'database': 'limitdb', 'table_name': 'coord_tweets', 'quality_function': 'PH', 'word': 'soccer'},
    {'database': 'limitdb1', 'table_name': 'coord_tweets', 'quality_function': 'PH', 'word': 'soccer'},
    {'database': 'limitdb2', 'table_name': 'coord_tweets', 'quality_function': 'PH', 'word': 'soccer'}
]
x_label = 'K Percentage (%)'
y_label = 'Quality'
title = 'K-Q curves of "soccer" on different data size'

# 2. Get the curves from corresponding database
db = None
curves = []
for targetCurve in targetCurves:
    database = targetCurve['database']
    if db is None:
        db = DatabaseFactory.getDatabase(dbtype, database)
    elif db.getDatabase() != database:
        db.close()
        db = DatabaseFactory.getDatabase(dbtype, database)

    curve = db.queryCurve(targetCurve['table_name'], targetCurve['quality_function'], targetCurve['word'])
    curves.append(curve)

print curves
# 3. plot the curves
PlotUtil.plotCurves(pdfBasePath + '/' + fileName, labels, x, curves, x_label, y_label, title)

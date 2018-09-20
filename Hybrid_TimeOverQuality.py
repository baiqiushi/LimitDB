# Time Over Quality
# For a given keyword and target quality,
# get a list of (r, k) value pairs that can satisfy this quality requirement
# and then run hybrid queries for different (r, k) pairs
# and draw T curves of different (r, k) pairs in one canvas
import time
import Conf
import DatabaseFactory
import KeywordsUtil
import Modeler
import PlotUtil
import numpy as np
import json

###########################################################
#   Configurations
###########################################################
dbType = Conf.DBTYPE
databaseName = Conf.DATABASE
tableName = Conf.TABLE

db = DatabaseFactory.getDatabase(dbType)

# From what frequency, choose keywords
frequencies = [5554384]
# For each frequency, how many keywords we choose
numOfKeywords = 1

# Target Quality
quality = 0.85

reversed_order = False

# Choose keywords with different frequencies
keywords = []
for freq in frequencies:
    keywords.extend(KeywordsUtil.pickNearestKeywordToFrequency(freq, numOfKeywords))
# Remove keywords with non alphabetic symbols
keywords[:] = [kw for kw in keywords if kw[0].isalpha()]
print keywords
# keywords = [('job', 495)]

r_percentages = range(10, 110, 10)
r_values = map(lambda rp: float(rp) / 100.0, r_percentages)
r_labels = map(lambda rp: str(rp) + '%', r_percentages)
keyword_labels = map(lambda kw: kw[0] + ':' + str(kw[1]), keywords)


###########################################################
#  Run Script
###########################################################
print '================================================='
print '  ' + dbType + '  Experiment - Time over quality '
print '- Hybrid approach'
print '================================================='
print 'table:', tableName
print 'keywords:', keywords
print 'r_percentage:', r_labels
print '-------------------------------------------------'
start = time.time()

# rk_pairs Dictionary stores for each keyword a list of list:
# {'soccer': [[r=R0,k=K0], [r=R1,k=K1], ..., [r=Rn,k=Kn]], 'rain': [[...]]}

# load rk_pairs dictionary from json file first
rk_pairs_file = dbType + '_' + databaseName + '_' + tableName + '_rk_pairs.json'
rk_pairs = {}
try:
    with open(rk_pairs_file) as f:
        rk_pairs = json.load(f)
except IOError:
    print rk_pairs_file, ' does not exist.'

# 1. Collect (r, k) pairs for each keyword that not in current dictionary
# For each keyword:
#   run Modeler.findKROfQuality() to get a list of (r, k) pairs

progress = 0
t0 = time.time()
for i_keyword in keywords:
    print 'Processing keyword =', i_keyword[0] + ' ...'
    if i_keyword[0] in rk_pairs.keys():
        print 'already exists in dictionary rk_pairs:', rk_pairs[i_keyword[0]]
    else:
        i_rk_pairs = Modeler.findKROfQuality(i_keyword[0], quality, r_values)
        rk_pairs[i_keyword[0]] = i_rk_pairs
    progress += 1
    print '[Total time]', time.time() - t0, \
        '[Progress]', str(progress * 100 / len(keywords)) + '%'

print rk_pairs

# Save rk_pairs dictionary into json file
with open(rk_pairs_file, 'w+') as f:
    json.dump(rk_pairs, f)

# 2. For each r value: (for one r value, there's only one k value respectively)
#      For each keyword, run hybrid query:
#        Send dummy query
#        Get the execution time of the query

# Time Dictionary stores for each keyword a list of Time
# {'soccer': [t(r=R0), t(r=R1), ...], 'rain': [...]}

# load times dictionary from json file first
times_file = 'hybrid_' + tableName + '_freq-' + str(min(frequencies)) + '-' + str(max(frequencies)) + '_q-' + str(quality) + '_times.json'
times = {}
draw_curves_directly = False
try:
    with open(times_file) as f:
        times = json.load(f)
        draw_curves_directly = True
except IOError:
    print times_file, ' does not exist.'
    # if json file does not exist, new an empty dictionary
    for keyword in keywords:
        times[keyword[0]] = [np.nan] * len(r_values)
print times

if not draw_curves_directly:
    progress = 0
    t0 = time.time()

    i_start = 0
    i_end = len(r_values)
    i_step = 1
    # run the queries in reversed order
    if reversed_order:
        i_start = len(r_values) - 1
        i_end = -1
        i_step = -1

    for i in range(i_start, i_end, i_step):

        # Restart DB
        db.restart()

        r = r_values[i]
        print 'Processing r =', str(int(r * 100)) + '% ...'
        for keyword in keywords:

            i_rk_pairs = rk_pairs[keyword[0]]
            k = i_rk_pairs[i][1]
            # if k value for this r for this keyword,
            # assign the time to be NaN
            if k < 0:
                times[keyword[0]][i] = np.nan
                continue

            # Send a dummy query
            t1 = time.time()
            db.queryDummy()
            t2 = time.time()
            print 'dummy query takes', t2 - t1, 's'

            # Send a warm up query
            t1 = time.time()
            db.queryWarmUp(tableName, keyword[0])
            t2 = time.time()
            print 'warm up query takes', t2 - t1, 's'

            t_start = time.time()
            l_coordinates_hybrid = db.GetCoordinateHybrid(tableName, keyword[0], r, k)
            t_end = time.time()
            print 'This query takes', t_end - t_start, 's'

            times[keyword[0]][i] = t_end - t_start

            progress += 1
            print '[Total time]', time.time() - t0, \
                '[Progress]', str(progress * 100 / (len(keywords) * len(r_values))) + '%'

    print times
    # Save times into json file

    with open(times_file, 'w+') as f:
        json.dump(times, f)

# 3. Plot the T-(r, k) curves of different keywords in one canvas
print 'Plotting images ...'
i_fileName_head = 'hybrid_' + tableName + '_freq-' + str(min(frequencies)) + '-' + str(max(frequencies)) + '_q-' + str(quality)

# (1) Plot T-(r, k) curves of different keywords
i_fileName = i_fileName_head + '_t-r-k'
i_labels = keyword_labels
print 'i_labels:'
print i_labels
i_x = r_labels
i_curves = []
print 'keywords:'
for keyword in keywords:
    print keyword[0]
    i_curves.append(times[keyword[0]])
i_x_label = '(r, k) pair for r'
i_y_label = 'Execution Time(s)'
i_title = 'F=[' + str(min(frequencies)) + '-' + str(max(frequencies)) + '] Q=' + str(quality) + ' - T-(r,k) curves'
print 'Plotting', i_title
PlotUtil.plotCurves(i_fileName, i_labels, i_x, i_curves, i_x_label, i_y_label, i_title)

end = time.time()
print '================================================='
print '  ' + dbType + '  Experiment - Time over quality '
print '- Hybrid approach'
print '================================================='
print 'table:', tableName
print 'keywords:', keywords
print 'r_percentage:', r_labels
print '-------------------------------------------------'
print 'Finished!', end - start, 'seconds spent.'

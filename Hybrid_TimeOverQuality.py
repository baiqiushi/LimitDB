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

###########################################################
#   Configurations
###########################################################
database = Conf.DATABASE
tableName = Conf.TABLE

db = DatabaseFactory.getDatabase(database)

# From what frequency, choose keywords
frequency = 50000
# For each frequency, how many keywords we choose
numOfKeywords = 20

# Target Quality
quality = 0.85

keywords = KeywordsUtil.pickNearestKeywordToFrequency(frequency, numOfKeywords)
print keywords
# keywords = [('job', 495)]

r_percentages = range(50, 110, 10)
r_values = map(lambda rp: float(rp) / 100.0, r_percentages)
r_labels = map(lambda rp: str(rp) + '%', r_percentages)
keyword_labels = map(lambda kw: kw[0] + ':' + str(kw[1]), keywords)


###########################################################
#  Run Script
###########################################################
print '================================================='
print '  ' + database + '  Experiment - Time over quality '
print '- Hybrid approach'
print '================================================='
print 'table:', tableName
print 'keywords:', keywords
print 'r_percentage:', r_labels
print '-------------------------------------------------'
start = time.time()

# 1. Collect (r, k) pairs for each keyword
# For each keyword:
#   run Modeler.findKROfQuality() to get a list of (r, k) pairs

# rk_pairs Dictionary stores for each keyword a list of list:
# {'soccer': [[r=R0,k=K0], [r=R1,k=K1], ..., [r=Rn,k=Kn]], 'rain': [[...]]}
rk_pairs = {}

progress = 0
t0 = time.time()
for i_keyword in keywords:
    print 'Processing keyword =', i_keyword[0] + ' ...'
    i_rk_pairs = Modeler.findKROfQuality(i_keyword[0], quality, r_values)
    rk_pairs[i_keyword[0]] = i_rk_pairs
    progress += 1
    print '[Total time]', time.time() - t0, \
        '[Progress]', str(progress * 100 / len(keywords)) + '%'

print rk_pairs

db.restart()
db.queryDummy()

# 2. For each r value: (for one r value, there's only one k value respectively)
#      For each keyword, run hybrid query:
#        Send dummy query
#        Get the execution time of the query

# Time Dictionary stores for each keyword a list of Time
# {'soccer': [t(r=R0), t(r=R1), ...], 'rain': [...]}
times = {}
for keyword in keywords:
    times[keyword[0]] = []
print times

progress = 0
t0 = time.time()
for i in range(0, r_values, 1):
    r = r_values[i]
    print 'Processing r =', str(int(r * 100)) + '% ...'
    for keyword in keywords:

        i_rk_pairs = rk_pairs[keyword[0]]
        k = i_rk_pairs[i][1]
        # if k value for this r for this keyword,
        # assign the time to be 0.0
        if k < 0:
            times[keyword[0]].append(0.0)
            continue

        # Send a dummy query
        db.queryDummy()

        t_start = time.time()
        l_coordinates_hybrid = db.GetCoordinateHybrid(tableName, keyword[0], r, k)
        t_end = time.time()

        times[keyword[0]].append(t_end - t_start)

        progress += 1
        print '[Total time]', time.time() - t0, \
            '[Progress]', str(progress * 100 / (len(keywords) * len(r_values))) + '%'

print times

# 3. Plot the T-(r, k) curves of different keywords in one canvas
print 'Plotting images ...'
i_fileName_head = 'freq=' + str(frequency) + '_q=' + str(quality)

# (1) Plot T-(r, k) curves of different keywords
i_fileName = i_fileName_head + '_t_(r-k)'
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
i_title = 'Frequency=' + str(frequency) + ' Quality=' + str(quality) + ' - T-(r,k) curves of different keywords'
print 'Plotting', i_title
PlotUtil.plotCurves(i_fileName, i_labels, i_x, i_curves, i_x_label, i_y_label, i_title)

end = time.time()
print '================================================='
print '  ' + database + '  Experiment - Time over quality '
print '- Hybrid approach'
print '================================================='
print 'table:', tableName
print 'keywords:', keywords
print 'r_percentage:', r_labels
print '-------------------------------------------------'
print 'Finished!', end - start, 'seconds spent.'

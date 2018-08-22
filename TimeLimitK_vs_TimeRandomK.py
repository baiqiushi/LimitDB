import matplotlib
matplotlib.use('Agg')
import time
import Conf
import DatabaseFactory
import KeywordsUtil
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt

###########################################################
#   Configurations
###########################################################
database = Conf.DATABASE
tableName = Conf.TABLE

db = DatabaseFactory.getDatabase(database)

# Choose 2 specific keywords
keywords = [KeywordsUtil.pickAllInFrequencyRange(990000, 1000000)[0]]  # work

# keywords = [('job', 495)]

k_percentages = [30, 50, 70, 80, 90]


# plot given p_curves1 all as one series in color blue and p_curves2 all as one series in color red into one image
# p_curves1: in the format as {x0: y0, x1: y1, ...}
# p_curves2: same as p_curves1
def plot2SeriesCurves(p_fileName, p_label1, p_curves1, p_label2, p_curves2, p_title, p_showLegend=True):
    pp = PdfPages(p_fileName + '.pdf')
    plt.figure()
    plt.plot(p_curves1.keys(), p_curves1.values(), 'bo-', label=p_label1)
    plt.plot(p_curves2.keys(), p_curves2.values(), 'ro-', label=p_label2)
    plt.xlabel('K Percentages')
    plt.ylabel('Time(s)')
    plt.title(p_title)
    plt.grid(True)
    if p_showLegend:
        plt.legend()
    plt.savefig(pp, format='pdf')
    pp.close()


###########################################################
#  Run Script
###########################################################
print '================================================='
print '  ' + database + '  Experiments - Time limit K vs random K'
print '================================================='
print 'table:', tableName
print 'keywords:', keywords
print 'k_percentage:', map(lambda k_p: str(k_p) + '%', k_percentages)
print '-------------------------------------------------'
start = time.time()

# 1.Get total coordinates for each keyword
# {'soccer': [coordinates], 'home': [coordinates]}
print 'Collecting total coordinates for all keywords ...'
totalCoordinates = {}
for keyword in keywords:
    totalCoordinates[keyword[0]] = db.GetCoordinate(tableName, keyword[0], -1)

# 2. Run same query for each keyword 3 times and average the time
# {'soccer': {30: time, 50: time, ...}, 'home': {...}}
time_random = {}
time_limit = {}
for keyword in keywords:
    time_random[keyword[0]] = {}
    time_limit[keyword[0]] = {}

print 'Start running queries with random k percentages ...'
progress = 0
t0 = time.time()
for i in range(0, 3, 1):
    for k_p in k_percentages:
        for keyword in keywords:
            l_random_ratio = float(k_p) / 100.0

            t_start = time.time()
            l_coordinates_random = db.GetCoordinateRandomly(tableName, keyword[0], l_random_ratio)
            t_end = time.time()

            l_time_random = t_end - t_start
            if k_p not in time_random[keyword[0]]:
                time_random[keyword[0]][k_p] = 0.0
            time_random[keyword[0]][k_p] += l_time_random

            # The last time, calculate the average
            if i == 2:
                time_random[keyword[0]][k_p] = time_random[keyword[0]][k_p] / 3.0

            progress += 1
            print '[Total time]', time.time() - t0, \
                '[Progress]', str(progress * 50 / (len(keywords) * len(k_percentages) * 3)) + '%'

        print 'sending dummy query ...'
        db.queryDummy()

    print 'restarting DB ...'
    db.restart()

print 'Start running queries with limit k percentages ...'
progress = 0
for i in range(0, 3, 1):
    for k_p in k_percentages:
        for keyword in keywords:
            l_limit_k = int(float(k_p) * len(totalCoordinates[keyword[0]]) / 100.0)

            t_start = time.time()
            l_coordinates_limit = db.GetCoordinate(tableName, keyword[0], l_limit_k)
            t_end = time.time()

            l_time_limit = t_end - t_start
            if k_p not in time_limit[keyword[0]]:
                time_limit[keyword[0]][k_p] = 0.0
            time_limit[keyword[0]][k_p] += l_time_limit

            # The last time, calculate the average
            if i == 2:
                time_limit[keyword[0]][k_p] = time_limit[keyword[0]][k_p] / 3.0

            progress += 1
            print '[Total time]', time.time() - t0, \
                '[Progress]', str(progress * 50 / (len(keywords) * len(k_percentages) * 3) + 50) + '%'

            print 'restarting DB ...'
            db.restart()

        print 'restarting DB ...'
        db.restart()

    print 'restarting DB ...'
    db.restart()


# 3. Plot the times in one canvas for each keyword
print 'Plotting images ...'
for keyword in keywords:
    i_fileName = 'time_' + keyword[0] + '_' + str(keyword[1])
    plot2SeriesCurves(i_fileName, 'random', time_random[keyword[0]],
                      'limit', time_limit[keyword[0]],
                      'Time - Keyword "' + keyword[0] + '"')

end = time.time()
print '================================================='
print '  ' + database + '  Experiments - Time limit K vs random K'
print '================================================='
print 'table:', tableName
print 'keywords:', keywords
print 'k_percentage:', map(lambda k_p: str(k_p) + '%', k_percentages)
print '-------------------------------------------------'
print 'Finished!', end - start, 'seconds spent.'

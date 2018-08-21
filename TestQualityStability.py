import matplotlib
matplotlib.use('Agg')
import time
import Conf
import DatabaseFactory
import KeywordsUtil
import QualityUtil
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt

###########################################################
#   Configurations
###########################################################
database = Conf.DATABASE
tableName = Conf.TABLE

db = DatabaseFactory.getDatabase(database)

# Choose 6 specific keywords
keywords = [KeywordsUtil.pickAllInFrequencyRange(5418, 5419)[0],  # soccer
            KeywordsUtil.pickAllInFrequencyRange(106875, 106877)[0],  # rain
            KeywordsUtil.pickAllInFrequencyRange(211000, 212000)[0],  # love
            KeywordsUtil.pickAllInFrequencyRange(500000, 600000)[0],  # appli
            KeywordsUtil.pickAllInFrequencyRange(990000, 1000000)[0]]  # work

k_percentages = [30, 50, 70, 90]


# plot given p_curves into one image
# p_curves: in the format as {label0: [y0, y1, ..., y19], label1: [y0, y1, ..., y19], ...}
def plotCurves(p_fileName, p_curves, p_title, p_showLegend=True):
    pp = PdfPages(p_fileName + '.pdf')
    plt.figure()
    for i_label in p_curves.keys():
        print i_label
        print p_curves[i_label]
        plt.plot(range(1, 21, 1), p_curves[i_label], label=( str(i_label) + '%'))
    plt.xlabel('the (i)th run')
    plt.ylabel('Quality(%)')
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
print '  ' + database + '  Experiments - Test Quality Stability'
print '- Random Function'
print '================================================='
print 'table:', tableName
print 'keywords:', keywords
print 'k_percentage:', map(lambda k_p: str(k_p) + '%', k_percentages)
QualityUtil.printInfo()
print '-------------------------------------------------'
start = time.time()

# 1.Get total coordinates for each keyword
# {'soccer': [coordinates], 'home': [coordinates]}
print 'Collecting total coordinates for all keywords ...'
totalCoordinates = {}
for keyword in keywords:
    totalCoordinates[keyword[0]] = db.GetCoordinate(tableName, keyword[0], -1)

# 2. Run same query for each keyword 20 times and calculate the quality
# {'soccer': {30: [20 qualities], 50: [20 qualities], ...}, 'home': {...}}
qualities = {}
for keyword in keywords:
    qualities[keyword[0]] = {}

print 'Start running queries with random k percentages ...'
progress = 0
t0 = time.time()
for i in range(0, 20, 1):
    for k_p in k_percentages:
        for keyword in keywords:
            l_random_ratio = float(k_p) / 100.0
            l_coordinates = db.GetCoordinateRandomly(tableName, keyword[0], l_random_ratio)
            l_quality = QualityUtil.phQualityOfCoordinates(totalCoordinates[keyword[0]], l_coordinates)
            if k_p not in qualities[keyword[0]]:
                qualities[keyword[0]][k_p] = []
            qualities[keyword[0]][k_p].append(l_quality * 100)
            progress += 1
            print '[Total time]', time.time() - t0, \
                '[Progress]', str(progress * 100 / (len(keywords) * len(k_percentages) * 20)) + '%'

# 3. Plot the qualities in one canvas for each keyword
print 'Plotting images ...'
for keyword in keywords:
    i_fileName = keyword[0] + '_' + keyword[1]
    plotCurves(i_fileName, qualities[keyword[0]], 'Random Function Qualities Stability - Keyword "' + keyword[0] + '"')

end = time.time()
print '================================================='
print '  ' + database + '  Experiments - Test Quality Stability'
print '- Random Function'
print '================================================='
print 'table:', tableName
print 'keywords:', keywords
print 'k_percentage:', map(lambda k_p: str(k_p) + '%', k_percentages)
QualityUtil.printInfo()
print '-------------------------------------------------'
print 'Finished!', end - start, 'seconds spent.'

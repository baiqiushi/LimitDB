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
        plt.plot(range(1, 21, 1), p_curves[i_label], label=(str(i_label) + '%'))
    plt.xlabel('the (i)th run')
    plt.ylabel('Quality(%)')
    plt.title(p_title)
    plt.grid(True)
    if p_showLegend:
        plt.legend()
    plt.savefig(pp, format='pdf')
    pp.close()


# plot given p_curves1 all as one series in color blue and p_curves2 all as one series in color red into one image

# p_curves1: in the format as {label0: [y0, y1, ..., y19], label1: [y0, y1, ..., y19], ...}
# p_curves2: same as p_curves1
def plot2SeriesCurves(p_fileName, p_label1, p_curves1, p_label2, p_curves2, p_title, p_showLegend=True):
    pp = PdfPages(p_fileName + '.pdf')
    plt.figure()
    i1 = 0
    for i_label in p_curves1.keys():
        i1 += 1
        # assign label only once
        if i1 == 1:
            plt.plot(range(1, 21, 1), p_curves1[i_label], 'bo-', label=p_label1)
        else:
            plt.plot(range(1, 21, 1), p_curves1[i_label], 'bo-')
    i2 = 0
    for i_label in p_curves2.keys():
        i2 += 1
        # assign label only once
        if i2 == 1:
            plt.plot(range(1, 21, 1), p_curves2[i_label], 'ro-', label=p_label2)
        else:
            plt.plot(range(1, 21, 1), p_curves2[i_label], 'ro-')
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
qualities_random = {}
qualities_limit = {}
for keyword in keywords:
    qualities_random[keyword[0]] = {}
    qualities_limit[keyword[0]] = {}

print 'Start running queries with random k percentages ...'
progress = 0
t0 = time.time()
for i in range(0, 20, 1):
    for k_p in k_percentages:
        for keyword in keywords:
            l_random_ratio = float(k_p) / 100.0
            l_limit_k = int(float(k_p) * keyword[1] / 100.0)
            l_coordinates_random = db.GetCoordinateRandomly(tableName, keyword[0], l_random_ratio)
            l_coordinates_limit = db.GetCoordinate(tableName, keyword[0], l_limit_k)
            l_quality_random = QualityUtil.phQualityOfCoordinates(totalCoordinates[keyword[0]], l_coordinates_random)
            l_quality_limit = QualityUtil.phQualityOfCoordinates(totalCoordinates[keyword[0]], l_coordinates_limit)
            if k_p not in qualities_random[keyword[0]]:
                qualities_random[keyword[0]][k_p] = []
            if k_p not in qualities_limit[keyword[0]]:
                qualities_limit[keyword[0]][k_p] = []
            qualities_random[keyword[0]][k_p].append(l_quality_random * 100)
            qualities_limit[keyword[0]][k_p].append(l_quality_limit * 100)
            progress += 1
            print '[Total time]', time.time() - t0, \
                '[Progress]', str(progress * 100 / (len(keywords) * len(k_percentages) * 20)) + '%'

# 3. Plot the qualities in one canvas for each keyword
print 'Plotting images ...'
for keyword in keywords:
    i_fileName = keyword[0] + '_' + str(keyword[1])
    plot2SeriesCurves(i_fileName, 'random', qualities_random[keyword[0]],
                      'limit', qualities_limit[keyword[0]],
                      'Qualities Stability - Keyword "' + keyword[0] + '"')

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

# Time Over R
# For a given k absolute value, plot T-r curves of different keywords in once canvas
import matplotlib
matplotlib.use('Agg')
import time
import Conf
import DatabaseFactory
import KeywordsUtil
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import numpy as np

###########################################################
#   Configurations
###########################################################
database = Conf.DATABASE
tableName = Conf.TABLE

db = DatabaseFactory.getDatabase(database)

# From what frequency, choose keywords
frequencies = [20000, 30000, 40000, 50000]
# For each frequency, how many keywords we choose
numOfKeywords = 10


# Choose keywords with different frequencies
keywords = []
for freq in frequencies:
    keywords.extend(KeywordsUtil.pickNearestKeywordToFrequency(freq, numOfKeywords))
print keywords
# keywords = [('job', 495)]

k_values = [10000, 15000, 20000, 25000, 30000, 35000, 40000]  # range(5000, 100000, 5000)
r_percentages = range(10, 110, 10)
r_labels = map(lambda rp: str(rp) + '%', r_percentages)


# plot given p_curves into one image
# p_labels: a list of labels with same order of list of curves in p_curves, format ['label0', 'label1', ..., 'labelN']
# p_x: a list of x axis values with same order of list of curves in p_curves, format [x0, x1, x2, ..., xM]
# p_curves: in the format as [[y0, y1, y2, ..., yM](curve0), [y0, y1, y2, ..., yM](curve1), ..., (curveN)]
#           a list of list, totally N curves, for each curve there're M values
# p_x_label: label for x axis
# p_y_label: label for y axis
def plotCurves(p_fileName, p_labels, p_x, p_curves, p_x_label, p_y_label, p_title, p_showLegend=True):
    pp = PdfPages(p_fileName + '.pdf')
    plt.figure()
    n = 0
    for i_label in p_labels:
        plt.plot(p_x, p_curves[n], label=i_label)
        n += 1
    plt.xlabel(p_x_label)
    plt.ylabel(p_y_label)
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
print '  ' + database + '  Experiment - Time over r value '
print '- Hybrid approach'
print '================================================='
print 'table:', tableName
print 'keywords:', keywords
print 'k_values:', k_values
print 'r_percentage:', r_labels
print '-------------------------------------------------'
start = time.time()

# 1. For each r value:
#      For each k value:
#        For each keyword, run hybrid query:
#          Send dummy query
#          Get the execution time of the query

# Time Dictionary stores for each keyword a 2D array, with i->r, j->k, and [i][j]->Time
# {'soccer': [[t(r=R0,k=K0), t(r=R0,k=K1), ...], [t(r=R1,k=K0), t(r=R1,k=K1), ...]], 'rain': [[...]]}
times = {}
for keyword in keywords:
    times[keyword[0]] = []
    m = 0
    for row in r_percentages:
        times[keyword[0]].append([])
        for col in k_values:
            times[keyword[0]][m].append(0)
        m += 1

print times

progress = 0
t0 = time.time()
i = 0
for r_p in r_percentages:
    print 'Processing r =', str(r_p) + '% ...'
    j = 0
    for k in k_values:
        print '    Processing k =', str(k) + ' ...'
        for keyword in keywords:
            # Send a dummy query
            db.queryDummy()

            l_random_r = float(r_p) / 100.0
            l_limit_k = k

            t_start = time.time()
            l_coordinates_hybrid = db.GetCoordinateHybrid(tableName, keyword[0], l_random_r, l_limit_k)
            t_end = time.time()

            times[keyword[0]][i][j] = t_end - t_start

            progress += 1
            print '[Total time]', time.time() - t0, \
                '[Progress]', str(progress * 100 / (len(keywords) * len(k_values) * len(r_percentages))) + '%'
        j += 1
    i += 1

print times

# 3. Plot the T-r curves of different keywords in one canvas per k value
print 'Plotting images ...'
for i in range(0, len(k_values), 1):
    k = k_values[i]
    i_fileName_head = 'k=' + str(k)
    # (1) Plot T-r curves of different keywords
    i_fileName = i_fileName_head + '_t_r'
    i_x = r_percentages
    i_labels = []
    i_curves = []
    print 'keywords:'
    for keyword in keywords:
        if keyword[1] * 0.9 <= k:
            continue
        print keyword[0]
        i_labels.append(keyword[0] + ':' + str(keyword[1]))
        i_curve = np.array(times[keyword[0]])[:, i]
        i_curves.append(i_curve)
    print i_curves
    print 'i_labels:'
    print i_labels
    i_x_label = 'Random r(%)'
    i_y_label = 'Execution Time(s)'
    i_title = 'k=' + str(k) + ' - T-r curves of different keywords'
    print 'Plotting', i_title
    plotCurves(i_fileName, i_labels, i_x, i_curves, i_x_label, i_y_label, i_title)

end = time.time()
print '================================================='
print '  ' + database + '  Experiments - Time over r value '
print '- Hybrid approach'
print '================================================='
print 'table:', tableName
print 'keywords:', keywords
print 'k_values:', k_values
print 'r_percentage:', r_labels
print '-------------------------------------------------'
print 'Finished!', end - start, 'seconds spent.'

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

# Choose keywords with similar frequency
frequency = 50000
numOfKeywords = 10
keywords = KeywordsUtil.pickNearestKeywordToFrequency(frequency, 10)
print keywords
# keywords = [('job', 495)]

k_percentages = range(5, 100, 5)
r_percentages = [30, 60, 90]  # range(10, 110, 10)

keyword_labels = map(lambda k: k[0] + ':' + str(k[1]), keywords)
k_labels = map(lambda k_p: str(k_p) + '%', k_percentages)
r_labels = map(lambda r_p: str(r_p) + '%', r_percentages)


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
print '  ' + database + '  Experiment - Time over (r, k) value '
print '- Hybrid approach'
print '================================================='
print 'table:', tableName
print 'keywords:', keywords
print 'k_percentage:', k_labels
print 'r_percentage:', r_labels
print '-------------------------------------------------'
start = time.time()

# 1.Get cardinality for each keyword
# {'soccer': c1, 'rain': c2, ...}
print 'Collecting cardinalities for all keywords ...'
cardinalities = {}
for keyword in keywords:
    cardinalities[keyword[0]] = db.GetCount(tableName, keyword[0])
print cardinalities

# 2. For each r value:
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
        for col in k_percentages:
            times[keyword[0]][m].append(0)
        m += 1

print times

progress = 0
t0 = time.time()
i = 0
for r_p in r_percentages:
    print 'Processing r =', str(r_p) + '% ...'
    j = 0
    for k_p in k_percentages:
        print '    Processing k =', str(k_p) + '% ...'
        for keyword in keywords:
            # Send a dummy query
            db.queryDummy()

            l_random_r = float(r_p) / 100.0
            l_limit_k = int(float(k_p) * cardinalities[keyword[0]] / 100.0)

            t_start = time.time()
            l_coordinates_hybrid = db.GetCoordinateHybrid(tableName, keyword[0], l_random_r, l_limit_k)
            t_end = time.time()

            times[keyword[0]][i][j] = t_end - t_start

            progress += 1
            print '[Total time]', time.time() - t0, \
                '[Progress]', str(progress * 100 / (len(keywords) * len(k_percentages) * len(r_percentages))) + '%'
        j += 1
    i += 1

print times

# 3. Plot the T-k curves of different keywords in one canvas per r value
print 'Plotting images ...'
for i in range(0, len(r_percentages), 1):
    r = r_labels[i]
    i_fileName_head = 'freq=' + str(frequency) + '_r=' + str(r)
    # (1) Plot T-k curves of different keywords
    i_fileName = i_fileName_head + '_t_k'
    i_labels = keyword_labels
    print 'i_labels:'
    print i_labels
    i_x = k_percentages
    i_curves = []
    print 'keywords:'
    for keyword in keywords:
        print keyword[0]
        i_curve = np.array(times[keyword[0]])[i, :]
        i_curves.append(i_curve)
    i_x_label = 'Limit k(%)'
    i_y_label = 'Execution Time(s)'
    i_title = 'r=' + str(r) + ' - T-k curves of different keywords'
    print 'Plotting', i_title
    plotCurves(i_fileName, i_labels, i_x, i_curves, i_x_label, i_y_label, i_title)

end = time.time()
print '================================================='
print '  ' + database + '  Experiments - Time over (r, k) value '
print '- Hybrid approach'
print '================================================='
print 'table:', tableName
print 'keywords:', keywords
print 'k_percentage:', k_labels
print 'r_percentage:', r_labels
print '-------------------------------------------------'
print 'Finished!', end - start, 'seconds spent.'

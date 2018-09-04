# Time Over K
# For a given r value, Plot T-k curves of different keywords in one canvas
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
frequency = 50000
# For each frequency, how many keywords we choose
numOfKeywords = 10
# Using k percentage or k absolute values
usingKP = False
# if usingKP = False, the steps of k values
k_step = 5000

keywords = KeywordsUtil.pickNearestKeywordToFrequency(frequency, numOfKeywords)
print keywords
# keywords = [('job', 495)]

if usingKP:
    k_percentages = range(5, 100, 5)
else:
    k_values = range(k_step, frequency, k_step)

numOfKs = len(k_percentages) if usingKP else len(k_values)

r_percentages = [25, 50, 75, 100]  # range(10, 110, 10)

keyword_labels = map(lambda k: k[0] + ':' + str(k[1]), keywords)
k_labels = k_percentages if usingKP else k_values
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
print '  ' + database + '  Experiment - Time over k percentage / value '
print '- Hybrid approach'
print '================================================='
print 'table:', tableName
print 'keywords:', keywords
if usingKP:
    print 'k_percentage:', k_labels
else:
    print 'k_values:', k_values
print 'r_percentage:', r_labels
print '-------------------------------------------------'
start = time.time()

# Only when using k percentages, we need to get cardinalities of keywords
if usingKP:
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
        for n in range(0, numOfKs, 1):
            times[keyword[0]][m].append(0)
        m += 1

print times

progress = 0
t0 = time.time()
i = 0
for r_p in r_percentages:
    print 'Processing r =', str(r_p) + '% ...'
    j = 0
    # ks = k_percentages / k_values
    ks = k_percentages if usingKP else k_values
    for k in ks:
        print '    Processing k =', str(k) + ('% ...' if usingKP else ' ...')
        for keyword in keywords:
            # Send a dummy query
            db.queryDummy()

            l_random_r = float(r_p) / 100.0

            l_limit_k = int(float(k) * cardinalities[keyword[0]] / 100.0) if usingKP else k

            t_start = time.time()
            l_coordinates_hybrid = db.GetCoordinateHybrid(tableName, keyword[0], l_random_r, l_limit_k)
            t_end = time.time()

            times[keyword[0]][i][j] = t_end - t_start

            progress += 1
            print '[Total time]', time.time() - t0, \
                '[Progress]', str(progress * 100 / (len(keywords) * numOfKs * len(r_percentages))) + '%'
        j += 1
    i += 1

print times

# 3. Plot the T-k curves of different keywords in one canvas per r value
print 'Plotting images ...'
for i in range(0, len(r_percentages), 1):
    r = r_labels[i]
    i_fileName_head = 'freq=' + str(frequency) + '_r=' + str(r)
    # (1) Plot T-k curves of different keywords
    i_fileName = i_fileName_head + ('_t_kp' if usingKP else '_t_kv')
    i_labels = keyword_labels
    print 'i_labels:'
    print i_labels
    i_x = k_labels
    i_curves = []
    print 'keywords:'
    for keyword in keywords:
        print keyword[0]
        i_curve = np.array(times[keyword[0]])[i, :]
        i_curves.append(i_curve)
    i_x_label = 'Limit k(%)' if usingKP else 'Limit k'
    i_y_label = 'Execution Time(s)'
    i_title = 'r=' + str(r) + ' - T-k curves of different keywords'
    print 'Plotting', i_title
    plotCurves(i_fileName, i_labels, i_x, i_curves, i_x_label, i_y_label, i_title)

end = time.time()
print '================================================='
print '  ' + database + '  Experiments - Time over k percentage / value '
print '- Hybrid approach'
print '================================================='
print 'table:', tableName
print 'keywords:', keywords
if usingKP:
    print 'k_percentage:', k_labels
else:
    print 'k_values:', k_values
print 'r_percentage:', r_labels
print '-------------------------------------------------'
print 'Finished!', end - start, 'seconds spent.'

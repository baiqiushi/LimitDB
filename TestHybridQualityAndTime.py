import matplotlib
matplotlib.use('Agg')
import time
import Conf
import DatabaseFactory
import KeywordsUtil
import QualityUtil
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
import numpy as np

###########################################################
#   Configurations
###########################################################
database = Conf.DBTYPE
tableName = Conf.TABLE

db = DatabaseFactory.getDatabase(database)

# Choose 6 specific keywords
keywords = [KeywordsUtil.pickAllInFrequencyRange(5418, 5419)[0],  # soccer
            KeywordsUtil.pickAllInFrequencyRange(106875, 106877)[0],  # rain
            KeywordsUtil.pickAllInFrequencyRange(211000, 212000)[0],  # love
            KeywordsUtil.pickAllInFrequencyRange(500000, 600000)[0],  # appli
            KeywordsUtil.pickAllInFrequencyRange(990000, 1000000)[0],  # work
            KeywordsUtil.pickAllInFrequencyRange(3000000, 4000000)[0]]  # job

# keywords = [('job', 495)]

k_percentages = range(5, 100, 5)
r_percentages = range(10, 110, 10)

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


def plotSurface(p_fileName, p_x, p_y, p_z, p_x_label, p_y_label, p_z_label, p_title, p_angle):
    pp = PdfPages(p_fileName + '.pdf')
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    ax.plot_surface(p_x, p_y, p_z, rstride=8, cstride=8, alpha=0.3)
    cset = ax.contour(p_x, p_y, p_z, zdir='z', cmap=cm.coolwarm)
    cset = ax.contour(p_x, p_y, p_z, zdir='x', cmap=cm.coolwarm)
    cset = ax.contour(p_x, p_y, p_z, zdir='y', cmap=cm.coolwarm)
    ax.set_xlabel(p_x_label)
    ax.set_ylabel(p_y_label)
    ax.set_zlabel(p_z_label)
    ax.view_init(30, p_angle)
    plt.title(p_title)
    plt.savefig(pp, format='pdf')
    pp.close()


###########################################################
#  Run Script
###########################################################
print '================================================='
print '  ' + database + '  Experiments - Draw Q-k and T-k curve for given r=R '
print '- Hybrid approach'
print '================================================='
print 'table:', tableName
print 'keywords:', keywords
print 'k_percentage:', k_labels
print 'r_percentage:', r_labels
QualityUtil.printInfo()
print '-------------------------------------------------'
start = time.time()

# 1.Get total coordinates for each keyword
# {'soccer': [coordinates], 'rain': [coordinates]}
print 'Collecting total coordinates for all keywords ...'
totalCoordinates = {}
for keyword in keywords:
    totalCoordinates[keyword[0]] = db.GetCoordinate(tableName, keyword[0], -1)

# 2. For each r value:
#      For each k value:
#        For each keyword, run hybrid query:
#          Send dummy query
#          Get the quality of the result
#          Get the execution time of the query

# Quality Dictionary stores for each keyword a 2D array, with i->r, j->k, and [i][j]->Quality
# {'soccer': [[q(r=R0,k=K0), q(r=R0,k=K1), ...], [q(r=R1,k=K0), q(r=R1,k=K1), ...]], 'rain': [[...]]}
qualities = {}
# Time Dictionary stores for each keyword a 2D array, with i->r, j->k, and [i][j]->Time
# {'soccer': [[t(r=R0,k=K0), t(r=R0,k=K1), ...], [t(r=R1,k=K0), t(r=R1,k=K1), ...]], 'rain': [[...]]}
times = {}
for keyword in keywords:
    qualities[keyword[0]] = []
    times[keyword[0]] = []
    m = 0
    for row in r_percentages:
        qualities[keyword[0]].append([])
        times[keyword[0]].append([])
        for col in k_percentages:
            qualities[keyword[0]][m].append(0)
            times[keyword[0]][m].append(0)
        m += 1

print qualities
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
            l_limit_k = int(float(k_p) * len(totalCoordinates[keyword[0]]) / 100.0)

            t_start = time.time()
            l_coordinates_hybrid = db.GetCoordinateHybrid(tableName, keyword[0], l_random_r, l_limit_k)
            t_end = time.time()

            l_quality = QualityUtil.phQualityOfCoordinates(totalCoordinates[keyword[0]], l_coordinates_hybrid)

            qualities[keyword[0]][i][j] = l_quality * 100
            times[keyword[0]][i][j] = t_end - t_start

            progress += 1
            print '[Total time]', time.time() - t0, \
                '[Progress]', str(progress * 100 / (len(keywords) * len(k_percentages) * len(r_percentages))) + '%'
        j += 1
    i += 1

print qualities
print times

# 3. Plot the Q-k / T-k curves of different r values in one canvas per each keyword
#    Plot the Q-r / T-r curves of different k values in one canvas per each keyword
#    Plot a 2D surface Q-(k,r) / T-(k,r) in one canvas per each keyword
print 'Plotting images ...'
for keyword in keywords:
    i_fileName_head = keyword[0] + '_' + str(keyword[1])
    # (1) Plot Q-k curves of different r
    i_fileName = i_fileName_head + '_q_k'
    i_labels = r_labels
    i_x = k_percentages
    i_curves = qualities[keyword[0]]
    i_x_label = 'Limit k(%)'
    i_y_label = 'Quality(%)'
    i_title = keyword[0] + ' - Q-k curves of different r'
    print 'Plotting', i_title
    plotCurves(i_fileName, i_labels, i_x, i_curves, i_x_label, i_y_label, i_title)

    # (2) Plot T-k curves of different r
    i_fileName = i_fileName_head + '_t_k'
    i_labels = r_labels
    i_x = k_percentages
    i_curves = times[keyword[0]]
    i_x_label = 'Limit k(%)'
    i_y_label = 'Execution Time(s)'
    i_title = keyword[0] + ' - T-k curves of different r'
    print 'Plotting', i_title
    plotCurves(i_fileName, i_labels, i_x, i_curves, i_x_label, i_y_label, i_title)

    # (3) Plot Q-r curves of different k
    i_fileName = i_fileName_head + '_q_r'
    i_labels = k_labels
    i_x = r_percentages
    i_curves = np.transpose(np.array(qualities[keyword[0]])).tolist()
    i_x_label = 'Random r (%)'
    i_y_label = 'Quality(%)'
    i_title = keyword[0] + ' - Q-r curves of different k'
    print 'Plotting', i_title
    plotCurves(i_fileName, i_labels, i_x, i_curves, i_x_label, i_y_label, i_title)

    # (4) Plot T-r curves of different k
    i_fileName = i_fileName_head + '_t_r'
    i_labels = k_labels
    i_x = r_percentages
    i_curves = np.transpose(np.array(times[keyword[0]])).tolist()
    i_x_label = 'Random r(%)'
    i_y_label = 'Execution Time(s)'
    i_title = keyword[0] + ' - T-r curves of different k'
    print 'Plotting', i_title
    plotCurves(i_fileName, i_labels, i_x, i_curves, i_x_label, i_y_label, i_title)

    # (5) Plot Q-k-r surface
    i_fileName = i_fileName_head + '_q_k_r_0.pdf'
    X, Y = np.meshgrid(k_percentages, r_percentages)
    Z = np.array(qualities[keyword[0]])
    i_x_label = 'Limit k(%)'
    i_y_label = 'Random r(%)'
    i_z_label = 'Quality(%)'
    i_title = keyword[0] + ' - Q-k-r surface'
    plotSurface(i_fileName, X, Y, Z, i_x_label, i_y_label, i_z_label, i_title, 0)

    i_fileName = i_fileName_head + '_q_k_r_90.pdf'
    plotSurface(i_fileName, X, Y, Z, i_x_label, i_y_label, i_z_label, i_title, 90)

    i_fileName = i_fileName_head + '_q_k_r_180.pdf'
    plotSurface(i_fileName, X, Y, Z, i_x_label, i_y_label, i_z_label, i_title, 180)

    i_fileName = i_fileName_head + '_q_k_r_270.pdf'
    plotSurface(i_fileName, X, Y, Z, i_x_label, i_y_label, i_z_label, i_title, 270)

    # (6) Plot T-k-r surface
    i_fileName = i_fileName_head + '_t_k_r_0.pdf'
    X, Y = np.meshgrid(k_percentages, r_percentages)
    Z = np.array(times[keyword[0]])
    i_x_label = 'Limit k(%)'
    i_y_label = 'Random r(%)'
    i_z_label = 'Execution Time(s)'
    i_title = keyword[0] + ' - T-k-r surface'
    plotSurface(i_fileName, X, Y, Z, i_x_label, i_y_label, i_z_label, i_title, 0)

    i_fileName = i_fileName_head + '_t_k_r_90.pdf'
    plotSurface(i_fileName, X, Y, Z, i_x_label, i_y_label, i_z_label, i_title, 90)

    i_fileName = i_fileName_head + '_t_k_r_180.pdf'
    plotSurface(i_fileName, X, Y, Z, i_x_label, i_y_label, i_z_label, i_title, 180)

    i_fileName = i_fileName_head + '_t_k_r_270.pdf'
    plotSurface(i_fileName, X, Y, Z, i_x_label, i_y_label, i_z_label, i_title, 270)


end = time.time()
print '================================================='
print '  ' + database + '  Experiments - Draw Q-k and T-k curve for given r=R '
print '- Hybrid approach'
print '================================================='
print 'table:', tableName
print 'keywords:', keywords
print 'k_percentage:', k_labels
print 'r_percentage:', r_labels
QualityUtil.printInfo()
print '-------------------------------------------------'
print 'Finished!', end - start, 'seconds spent.'

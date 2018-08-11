import csv
import Conf
import DatabaseFactory
import KeywordsUtil
import QualityUtil
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import time
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.cluster import KMeans

database = Conf.DATABASE
tableName = Conf.TABLE

# Keywords frequency range
min_freq = 5000
max_freq = 4000000

# GroupByFrequency
unit_freq = 5000
max_density = 100

# KMeans parameter
K = 100
# DBSCAN parameter
EPS = 0.3

db = DatabaseFactory.getDatabase(database)
keywords = KeywordsUtil.pickAllInFrequencyRange(min_freq, max_freq)

k_percentage = range(5, 100, 5)


# get the number of keywords in this frequency range
def getNumOfKeywords(p_min_freq, p_max_freq):
    results = [keyword for keyword in keywords if p_min_freq <= keyword[1] < p_max_freq]
    return len(results)


# get the curves data for given frequency range
# [keyword, frequency, q(5%), q(10%), ..., q(95%)]
def getCurvesOfKeywords(p_min_freq, p_max_freq):
    results = db.queryCurveInCount(p_min_freq, p_max_freq)
    return results


# get the curves data for given frequency range
# [keyword, frequency, q(5%), q(10%), ..., q(95%), len, mean, std, var]
def getAnalyzedCurvesOfKeywords(p_min_freq, p_max_freq):
    results = db.queryAnalyzedCurveInCount(p_min_freq, p_max_freq)
    return results


# plot given p_curves into one image
# p_curves: in the format as [keyword, frequency, q(5%), q(10%), ..., q(95%)]
def plotCurves(p_pp, p_curves, p_title, p_showLegend=True):
    plt.figure()
    for curve in p_curves:
        plt.plot(k_percentage, curve[2:21], label=(curve[0] + ":" + str(curve[1])))
    plt.xlabel('K Percentage')
    plt.ylabel('Quality')
    plt.title(p_title)
    plt.grid(True)
    if p_showLegend:
        plt.legend()
    plt.savefig(p_pp, format='pdf')


# group keywords by frequency natural boundaries
# p_min_freq, p_max_freq: frequency range of all keywords are grouped
# p_unit_Freq: the maximum difference of frequencies between adjacent groups
# p_max_density: threshold, if number of keywords in one group exceeds
#                p_max_density, divide the group into 2, repeat this
#                dividing until the density is within threshold
def groupByFrequency(p_min_freq, p_max_freq, p_unit_freq, p_max_density):

    pp = PdfPages('groupByFrequency.pdf')

    i = p_min_freq
    j = i + p_unit_freq
    t_compute = 0.0
    t_query = 0.0
    t_plot = 0.0
    l_numOfGroups = 0
    while j <= p_max_freq:
        t0 = time.time()
        l_density = getNumOfKeywords(i, j)
        t1 = time.time()
        t_compute += t1 - t0
        # divide the group into 2
        if l_density > p_max_density:
            j = i + int((j - i) / 2)
            continue
        elif l_density <= int(p_max_density/4):
            j = i + int((j - i) * 2)
            continue
        else:
            t2 = time.time()
            l_curves = getCurvesOfKeywords(i, j)
            t3 = time.time()
            t_query += t3 - t2
            l_title = 'Keywords with frequency in [' + str(i) + ', ' + str(j) + '] total ' + str(len(l_curves))
            print 'Plotting ==>', l_title
            plotCurves(pp, l_curves, l_title)
            t4 = time.time()
            t_plot += t4 - t3
            i = j
            j = i + p_unit_freq
            l_numOfGroups += 1
    pp.close()
    return l_numOfGroups, t_compute, t_query, t_plot


def plotKeywordsFrequencies():
    l_x = map(lambda kw: kw[1], keywords)
    l_y = [1] * len(l_x)
    plt.figure()
    plt.scatter(l_x, l_y)
    plt.show()


def groupByFrequencyDBSCAN():
    # array of frequencies of keywords
    l_freqs = np.array(map(lambda kw: [kw[1], 0], keywords)).reshape(-1, 1)
    print l_freqs
    l_dbscan = DBSCAN(eps=0.3).fit(l_freqs)
    print l_dbscan
    print l_dbscan.labels_
    print l_dbscan.components_
    print l_dbscan.core_sample_indices_


def groupByFrequencyKMeans(p_k=100):

    pp = PdfPages('groupByFrequencyKMeans.pdf')

    t_compute = 0.0
    t_query = 0.0
    t_plot = 0.0
    l_numOfGroups = p_k
    t0 = time.time()
    # array of frequencies of keywords
    l_keywords = keywords[::-1]
    l_freqs = np.array(map(lambda kw: kw[1], l_keywords)).reshape(-1, 1)
    # k-means clustering the keywords by frequencies
    l_km = KMeans(n_clusters=p_k)
    l_km.fit(l_freqs)
    t1 = time.time()
    t_compute += t1 - t0
    # plot the curves of each cluster from p_min_freq to p_max_freq
    # i, j are indexes of keywords in keywords and labels list
    i = 0
    j = i
    while j < len(l_km.labels_):
        l_group_label = l_km.labels_[i]
        l_x_label = l_km.labels_[j]
        while l_x_label == l_group_label:
            j += 1
            if j >= len(l_km.labels_):
                break
            l_x_label = l_km.labels_[j]
        j -= 1
        l_min_freq = l_keywords[i][1]
        l_max_freq = l_keywords[j][1]
        t2 = time.time()
        l_curves = getCurvesOfKeywords(l_min_freq, l_max_freq)
        t3 = time.time()
        t_query += t3 - t2
        l_title = 'Keywords with frequency in [' + str(l_min_freq) + ', ' + str(l_max_freq) + '] total '\
                  + str(len(l_curves))
        print 'Plotting ==>', l_title
        plotCurves(pp, l_curves, l_title)
        t4 = time.time()
        t_plot += t4 - t3
        i = j + 1
        j = i

    pp.close()
    return l_numOfGroups, t_compute, t_query, t_plot


def analyzeCurveByDensityAndSkewness(p_min_freq, p_max_freq):
    print "Start analyzing the curves of keywords [" + str(p_min_freq) + ", "\
          + str(p_max_freq) + "] by density and skewness......"
    # get all curves
    l_curves = getCurvesOfKeywords(p_min_freq, p_max_freq)
    # get mean, std, variation of each keyword's perfect image
    t0 = time.time()
    i = 0
    for curve in l_curves:
        i += 1
        print 'Analyzing progress ===> ' + str(i * 100 / len(l_curves)) + '%,  ' + str(time.time() - t0) + 's.'
        ar = np.array(db.GetCoordinate(tableName, curve[0], -1))
        if len(ar) == 0:
            l_len = 0
            l_mean = 0.0
            l_std = 0.0
            l_var = 0.0
        else:
            H = QualityUtil.coordinatesToImage(ar)
            # only keep the non zero cells
            nonZeroH = H[np.nonzero(H)]
            l_len = len(nonZeroH)
            l_mean = np.mean(nonZeroH)
            l_std = np.std(nonZeroH)
            l_var = np.var(nonZeroH)
        curve.extend([l_len, l_mean, l_std, l_var])
    print "Finished analyzing the curves of keywords [" + str(p_min_freq) + ", " \
          + str(p_max_freq) + "] by density and skewness !"
    writeOutCurves(l_curves, 'keyword_curves_analyzed.csv')
    return l_curves


def groupByDensityAndSkewnessKMeans(p_min_freq, p_max_freq, p_k=100):

    # get analyzed curves
    l_curves = analyzeCurveByDensityAndSkewness(p_min_freq, p_max_freq)

    # kmeans clustering by [mean, std] of each keyword
    l_vectors = np.array(map(lambda curve: [curve[22], curve[23]], l_curves))
    l_km = KMeans(n_clusters=p_k)
    l_km.fit(l_vectors)

    # plot the same labeled curves in one plot
    pp = PdfPages('groupByDensityAndSkewnessKMeans.pdf')
    plotCurvesByLabels(pp, l_curves, l_km.labels_)
    pp.close()

    # write the labeled curves to csv file
    l_labeled_curves = tagLabels(l_curves, l_km.labels_)
    writeOutCurves(l_labeled_curves, 'keyword_curves_grouped_density.csv')


def plotCurvesByLabels(p_pp, p_curves, p_labels):
    # plot the curves for each cluster
    for label in range(0, len(set(p_labels)), 1):
        l_label_curves = []
        for i in range(0, len(p_labels), 1):
            if p_labels[i] == label:
                l_label_curves.append(p_curves[i])
        plotCurves(p_pp, l_label_curves, str(label))


def tagLabels(p_curves, p_labels):
    for i in range(0, len(p_curves), 1):
        p_curves[i].append(p_labels[i])
    return p_curves


def writeOutCurves(p_curves, p_fileName):
    with open(p_fileName, 'w') as csvFile:
        csvWriter = csv.writer(csvFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for curve in p_curves:
            csvWriter.writerow(curve)


def groupByCurves(p_min_freq, p_max_freq, p_k=100, p_eps=0.3):
    # get all curves
    l_curves = getCurvesOfKeywords(p_min_freq, p_max_freq)
    # get rid of word and count fields
    l_vector_curves = map(lambda cur: cur[2:20], l_curves)

    # 1. K-Means
    l_km = KMeans(n_clusters=p_k)
    l_km.fit(l_vector_curves)
    # plot the same labeled curves in one plot
    pp = PdfPages('groupByCurvesKMeans.pdf')
    plotCurvesByLabels(pp, l_curves, l_km.labels_)
    pp.close()

    # 2. DBSCAN
    l_dbscan = DBSCAN(eps=0.1)
    l_dbscan.fit(l_vector_curves)
    l_numOfGroups = len(set(l_dbscan.labels_)) - (1 if -1 in l_dbscan.labels_ else 0)
    # plot the same labeled curves in one plot
    pp = PdfPages('groupByCurvesDBSCAN.pdf')
    plotCurvesByLabels(pp, l_curves, l_dbscan.labels_)
    pp.close()

    # 3. write the labeled curves to csv file
    # label K-Means
    l_labeled_curves = tagLabels(l_curves, l_km.labels_)
    # label DBSCAN
    l_labeled_curves = tagLabels(l_labeled_curves, l_dbscan.labels_)
    writeOutCurves(l_labeled_curves, 'keyword_curves_grouped.csv')

    return l_numOfGroups


print '================================================='
print '  ' + database + '  Experiments - 4.2 Keywords Grouping'
print 'Approach 1: Group by frequency natural boundaries'
print '================================================='
print 'table:', tableName
print 'frequency range:[', min_freq, ',', max_freq, ']'
print 'Unit frequency:', unit_freq
print 'Max density:', max_density
print '================================================='
start = time.time()
numOfGroups, computeTime, queryTime, plotTime = groupByFrequency(min_freq, max_freq, unit_freq, max_density)
end = time.time()
print '-------------------------------------------------'
print 'Approach 1 is done!'
print 'Total number of groups:', numOfGroups
print 'Time of computing:', computeTime
print 'Time of querying:', queryTime
print 'Time of plotting:', plotTime
print 'Total time:', end - start

print '================================================='
print '  ' + database + '  Experiments - 4.2 Keywords Grouping'
print 'Approach 2: Group by frequency clustering by K-Means'
print '================================================='
print 'table:', tableName
print 'frequency range:[', min_freq, ',', max_freq, ']'
print 'K:', K
print '================================================='
start = time.time()
numOfGroups, computeTime, queryTime, plotTime = groupByFrequencyKMeans(K)
end = time.time()
print '-------------------------------------------------'
print 'Approach 2 is done!'
print 'Total number of groups:', numOfGroups
print 'Time of computing:', computeTime
print 'Time of querying:', queryTime
print 'Time of plotting:', plotTime
print 'Total time:', end - start

print '================================================='
print '  ' + database + '  Experiments - 4.2 Keywords Grouping'
print 'Approach 3: Group by density and skewness clustering by K-Means'
print '================================================='
print 'table:', tableName
print 'frequency range:[', min_freq, ',', max_freq, ']'
print 'K:', K
print '================================================='
start = time.time()
groupByDensityAndSkewnessKMeans(min_freq, max_freq, K)
end = time.time()
print '-------------------------------------------------'
print 'Approach 3 is done!'
print 'Total number of groups:', K
print 'Total time:', end - start

print '================================================='
print '  ' + database + '  Experiments - 4.2 Keywords Grouping'
print 'Ground Truth : Group by curves clustering by K-Means & DBSCAN'
print '================================================='
print 'table:', tableName
print 'frequency range:[', min_freq, ',', max_freq, ']'
print 'K:', K
print 'eps:', EPS, "(maximum distance between two samples)"
print '================================================='
start = time.time()
dbscan_numOfGroups = groupByCurves(min_freq, max_freq, 100)
end = time.time()
print '-------------------------------------------------'
print 'Ground Truth is done!'
print 'Total number of groups for K-Means:', K
print 'Total number of groups for DBSCAN:', dbscan_numOfGroups
print 'Total time:', end - start

db.close()

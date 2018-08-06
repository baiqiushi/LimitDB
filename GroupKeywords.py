import Conf
import DatabaseFactory
import KeywordsUtil
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

# GroupByFrequecnyKMeans
K = 30


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


# plot given p_curves into one image
# p_curves: in the format as [keyword, frequency, q(5%), q(10%), ..., q(95%)]
def plotCurves(p_curves, p_title):
    plt.figure()
    for curve in p_curves:
        plt.plot(k_percentage, curve[2:21])
    plt.xlabel('K Percentage')
    plt.ylabel('Quality')
    plt.title(p_title)
    plt.grid(True)
    plt.savefig(pp, format='pdf')


# group keywords by frequency natural boundaries
# p_min_freq, p_max_freq: frequency range of all keywords are grouped
# p_unit_Freq: the maximum difference of frequencies between adjacent groups
# p_max_density: threshold, if number of keywords in one group exceeds
#                p_max_density, divide the group into 2, repeat this
#                dividing until the density is within threshold
def groupByFrequency(p_min_freq, p_max_freq, p_unit_freq, p_max_density):

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
            plotCurves(l_curves, l_title)
            t4 = time.time()
            t_plot += t4 - t3
            i = j
            j = i + p_unit_freq
            l_numOfGroups += 1
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
    l_dbscan = DBSCAN().fit(l_freqs)
    print l_dbscan
    print l_dbscan.labels_
    print l_dbscan.components_
    print l_dbscan.core_sample_indices_


def groupByFrequencyKMeans(p_min_freq, p_max_freq, p_k=30):
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
        l_x_label = l_km.labels_[i]
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
        plotCurves(l_curves, l_title)
        t4 = time.time()
        t_plot += t4 - t3
        i = j + 1
        j = i
    return l_numOfGroups, t_compute, t_query, t_plot


print '================================================='
print '  ' + database + '  Experiments - 4.2 Keywords Grouping'
print '================================================='
print 'table:', tableName
print 'frequency range:[', min_freq, ',', max_freq, ']'
print '================================================='
print 'Approach 1: Group by frequency natural boundaries'
print 'Unit frequency:', unit_freq
print 'Max density:', max_density
pp = PdfPages('groupByFrequency.pdf')
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
pp.close()

print '================================================='
print '  ' + database + '  Experiments - 4.2 Keywords Grouping'
print '================================================='
print 'table:', tableName
print 'frequency range:[', min_freq, ',', max_freq, ']'
print '================================================='
print 'Approach 2: Group by frequency clustering by K-Means'
print 'K:', K
pp = PdfPages('groupByFrequencyKMeans.pdf')
start = time.time()
numOfGroups, computeTime, queryTime, plotTime = groupByFrequencyKMeans(min_freq, max_freq, K)
end = time.time()
print '-------------------------------------------------'
print 'Approach 2 is done!'
print 'Total number of groups:', numOfGroups
print 'Time of computing:', computeTime
print 'Time of querying:', queryTime
print 'Time of plotting:', plotTime
print 'Total time:', end - start
pp.close()

db.close()

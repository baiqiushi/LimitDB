import matplotlib
matplotlib.use('Agg')
import csv
import Conf
import DatabaseFactory
import KeywordsUtil
import QualityUtil
from matplotlib.backends.backend_pdf import PdfPages
import time
import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt


###########################################################
#   Configurations
###########################################################
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
# How many curves are in one cluster
curve_density = 60

# Group by sample sub-curves
start_pk = 50
end_pk = 95

db = DatabaseFactory.getDatabase(database)
keywords = KeywordsUtil.pickAllInFrequencyRange(min_freq, max_freq)

k_percentage = range(5, 100, 5)
target_quality = range(70, 100, 5)


# get the number of keywords in this frequency range
def getNumOfKeywords(p_min_freq, p_max_freq):
    results = [keyword for keyword in keywords if p_min_freq <= keyword[1] < p_max_freq]
    return len(results)


# get the curves data for given frequency range
# [keyword, frequency, q(5%), q(10%), ..., q(95%)]
def getCurvesOfKeywords(p_min_freq, p_max_freq, p_curveTableName):
    results = db.queryCurveInCount(p_min_freq, p_max_freq, p_curveTableName)
    return results


# get the k values data for given frequency range
# [keyword, frequency, k(0.7), k(0.75), ......, k(0.95)]
def getKValuesOfKeywords(p_min_freq, p_max_freq, p_kValuesTableName):
    results = db.queryKValuesInCount(p_min_freq, p_max_freq, p_kValuesTableName)
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
        print k_percentage
        print curve[2:21]
        plt.plot(k_percentage, curve[2:21], label=(curve[0] + ":" + str(curve[1])))
    plt.xlabel('K Percentage')
    plt.ylabel('Quality')
    plt.title(p_title)
    plt.grid(True)
    if p_showLegend:
        plt.legend()
    plt.savefig(p_pp, format='pdf')


# plot given p_k_values into one image
# p_k_values: in the format as [keyword, frequency, k(0.7), k(0.75), ..., k(0.95)]
def plotKValues(p_pp, p_k_values, p_title, p_showLegend=True):
    plt.figure()
    for k_values in p_k_values:
        plt.plot(target_quality, k_values[2:8], label=(k_values[0] + ":" + str(k_values[1])))
    plt.xlabel('Target Quality')
    plt.ylabel('K Value')
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
    l_curveTableName = 'wordcurve'
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
            l_curves = getCurvesOfKeywords(i, j, l_curveTableName)
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


def groupByFrequencyKMeans(p_k=100):

    pp = PdfPages('groupByFrequencyKMeans.pdf')
    l_curveTableName = 'wordcurve'
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
        l_curves = getCurvesOfKeywords(l_min_freq, l_max_freq, l_curveTableName)
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
    l_curveTableName = 'wordcurve'
    l_curves = getCurvesOfKeywords(p_min_freq, p_max_freq, l_curveTableName)
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


def groupByFrequencyAndDensityAndSkewnessKMeans(p_min_freq, p_max_freq, p_k=100):

    # get analyzed curves
    l_curves = getAnalyzedCurvesOfKeywords(p_min_freq, p_max_freq)

    # kmeans clustering by [mean, std] of each keyword
    l_vectors = np.array(map(lambda curve: [curve[1], curve[22], curve[23]], l_curves))
    l_km = KMeans(n_clusters=p_k)
    l_km.fit(l_vectors)

    # plot the same labeled curves in one plot
    pp = PdfPages('groupByFrequencyAndDensityAndSkewnessKMeans.pdf')
    plotCurvesByLabels(pp, l_curves, l_km.labels_)
    pp.close()

    # write the labeled curves to csv file
    l_labeled_curves = tagLabels(l_curves, l_km.labels_)
    writeOutCurves(l_labeled_curves, 'keyword_curves_grouped_freq_density.csv')


def groupByCellLenAndDensityAndSkewnessKMeans(p_min_freq, p_max_freq, p_k=100):

    # get analyzed curves
    l_curves = getAnalyzedCurvesOfKeywords(p_min_freq, p_max_freq)

    # kmeans clustering by [mean, std] of each keyword
    l_vectors = np.array(map(lambda curve: [curve[21], curve[22], curve[23]], l_curves))
    l_km = KMeans(n_clusters=p_k)
    l_km.fit(l_vectors)

    # plot the same labeled curves in one plot
    pp = PdfPages('groupByCellLenAndDensityAndSkewnessKMeans.pdf')
    plotCurvesByLabels(pp, l_curves, l_km.labels_)
    pp.close()

    # write the labeled curves to csv file
    l_labeled_curves = tagLabels(l_curves, l_km.labels_)
    writeOutCurves(l_labeled_curves, 'keyword_curves_grouped_cell_len_density.csv')


def groupByFreqAndCellLenAndDensityAndSkewnessKMeans(p_min_freq, p_max_freq, p_k=100):

    # get analyzed curves
    l_curves = getAnalyzedCurvesOfKeywords(p_min_freq, p_max_freq)

    # kmeans clustering by [mean, std] of each keyword
    l_vectors = np.array(map(lambda curve: [curve[1], curve[21], curve[22], curve[23]], l_curves))
    l_km = KMeans(n_clusters=p_k)
    l_km.fit(l_vectors)

    # plot the same labeled curves in one plot
    pp = PdfPages('groupByFreqAndCellLenAndDensityAndSkewnessKMeans.pdf')
    plotCurvesByLabels(pp, l_curves, l_km.labels_)
    pp.close()

    # write the labeled curves to csv file
    l_labeled_curves = tagLabels(l_curves, l_km.labels_)
    writeOutCurves(l_labeled_curves, 'keyword_curves_grouped_freq_cell_len_density.csv')


def plotCurvesByLabels(p_pp, p_curves, p_labels):
    # plot the curves for each cluster
    for label in range(0, len(set(p_labels)), 1):
        l_label_curves = []
        for i in range(0, len(p_labels), 1):
            if p_labels[i] == label:
                l_label_curves.append(p_curves[i])
        plotCurves(p_pp, l_label_curves, "Group " + str(label) + ": " + str(len(l_label_curves)) + " keywords")


def plotKValuesByLabels(p_pp, p_k_values, p_labels):
    # plot the k_values for each cluster
    for label in range(0, len(set(p_labels)), 1):
        l_label_k_values = []
        for i in range(0, len(p_labels), 1):
            if p_labels[i] == label:
                l_label_k_values.append(p_k_values[i])
        plotKValues(p_pp, l_label_k_values, "Group " + str(label) + ": " + str(len(l_label_k_values)) + " keywords")


def tagLabels(p_curves, p_labels):
    for i in range(0, len(p_curves), 1):
        p_curves[i].append(p_labels[i])
    return p_curves


def writeOutCurves(p_curves, p_fileName):
    with open(p_fileName, 'w') as csvFile:
        csvWriter = csv.writer(csvFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for curve in p_curves:
            csvWriter.writerow(curve)


def groupByCurves(p_min_freq, p_max_freq, p_k=10):
    # get all curves
    l_curveTableName = 'wordcurve'
    l_curves = getCurvesOfKeywords(p_min_freq, p_max_freq, l_curveTableName)
    # get rid of word and count fields
    l_vector_curves = map(lambda cur: cur[2:21], l_curves)

    # 1. K-Means
    l_km = KMeans(n_clusters=p_k)
    l_km.fit(l_vector_curves)
    # plot the same labeled curves in one plot
    pp = PdfPages('groupCurves.pdf')
    plotCurvesByLabels(pp, l_curves, l_km.labels_)
    pp.close()

    # 2. write the labeled curves to csv file
    # label K-Means
    l_labeled_curves = tagLabels(l_curves, l_km.labels_)
    writeOutCurves(l_labeled_curves, 'keyword_curves_grouped.csv')


def groupBySampleCurves(p_min_freq, p_max_freq, p_start_kp, p_end_kp, p_k=10):
    # get all curves
    l_sampleCurveTableName = 'wordcurve_sample'
    l_sampleCurves = getCurvesOfKeywords(p_min_freq, p_max_freq, l_sampleCurveTableName)
    # get rid of word and count fields and get curve in range [p_start_kp, p_end_kp]
    l_start_index = k_percentage.index(p_start_kp) + 2
    l_end_index = k_percentage.index(p_end_kp) + 2
    l_vector_curves = map(lambda cur: cur[l_start_index:l_end_index + 1], l_sampleCurves)

    # 1. K-Means
    l_km = KMeans(n_clusters=p_k)
    l_km.fit(l_vector_curves)
    # plot the same labeled curves in one plot
    pp = PdfPages('groupSampleCurves_f' + str(p_min_freq) + '_f' + str(p_max_freq) + '_k' + str(p_k) + '_kp' + str(p_start_kp) + '.pdf')
    plotCurvesByLabels(pp, l_sampleCurves, l_km.labels_)
    pp.close()

    # 2. write the labeled curves to csv file
    # label K-Means
    l_labeled_curves = tagLabels(l_sampleCurves, l_km.labels_)
    writeOutCurves(l_labeled_curves, 'keyword_sample_curves_grouped_f' + str(p_min_freq) + '_f' + str(p_max_freq) + '_k' + str(p_k) + '_kp' + str(p_start_kp) + '.csv')

    # 3. plot the curves from original dataset based on clustering results on sample curves
    l_curveTableName = 'wordcurve'
    l_curves = getCurvesOfKeywords(p_min_freq, p_max_freq, l_curveTableName)
    pp = PdfPages('groupCurvesBySample_f' + str(p_min_freq) + '_f' + str(p_max_freq) + '_k' + str(p_k) + '_kp' + str(p_start_kp) + '.pdf')
    plotCurvesByLabels(pp, l_curves, l_km.labels_)
    pp.close()


def groupBySampleKValues(p_min_freq, p_max_freq, p_k=10):
    # get all sample k values
    l_sampleKValuesTableName = 'wordkvalues_sample'
    l_sampleKValues = getKValuesOfKeywords(p_min_freq, p_max_freq, l_sampleKValuesTableName)
    # get rid of word and count fields and get k values
    l_vector_k_values = map(lambda cur: cur[2:8], l_sampleKValues)

    # 1. K-Means
    l_km = KMeans(n_clusters=p_k)
    l_km.fit(l_vector_k_values)
    # plot the same labeled curves in one plot
    pp = PdfPages('groupSampleKValues_f' + str(p_min_freq) + '_f' + str(p_max_freq) + '_k' + str(p_k) + '.pdf')
    plotKValuesByLabels(pp, l_sampleKValues, l_km.labels_)
    pp.close()

    # 2. write the labeled k values to csv file
    # label K-Means
    l_labeled_k_values = tagLabels(l_sampleKValues, l_km.labels_)
    writeOutCurves(l_labeled_k_values, 'keyword_sample_k_values_grouped_f' + str(p_min_freq) + '_f' + str(p_max_freq) + '_k' + str(p_k) + '.csv')

    # 3. plot the curves from original dataset based on clustering results on sample k values
    l_curveTableName = 'wordcurve'
    l_curves = getCurvesOfKeywords(p_min_freq, p_max_freq, l_curveTableName)
    pp = PdfPages('groupCurvesBySampleKValues_f' + str(p_min_freq) + '_f' + str(p_max_freq) + '_k' + str(p_k) + '.pdf')
    plotCurvesByLabels(pp, l_curves, l_km.labels_)
    pp.close()

    # 4. plot the k values from original dataset based on clustering results on sample k values
    l_kValuesTableName = 'wordkvalues'
    l_kValues = getKValuesOfKeywords(p_min_freq, p_max_freq, l_kValuesTableName)
    pp = PdfPages(
        'groupKValuesBySampleKValues_f' + str(p_min_freq) + '_f' + str(p_max_freq) + '_k' + str(p_k) + '.pdf')
    plotKValuesByLabels(pp, l_kValues, l_km.labels_)
    pp.close()


# Use curves kmeans clustering results to clean the original curves
# Delete those curves that appears in a group containing less than 6 curves
def cleanCurves():
    sql = "delete from wordcurve g where g.word in " \
          "  (select t1.word from wordcurve_grouped t1 where t1.kmeans in " \
          "    (select o.kmeans from " \
          "      (select t.kmeans, count(*) as count from wordcurve_grouped t group by t.kmeans) o " \
          "    where o.count <= 6))"
    return sql


def jaccardSimilarity(list1, list2):

    if len(list1) == 0 | len(list2) == 0:
        return 0.0

    intersection = len(list(set(list1).intersection(list2)))
    # print(list(set(list1).intersection(list2)))
    # print "intersection = ", intersection
    union = (len(list1) + len(list2)) - intersection
    # print "union = ", union
    return intersection, union, float(intersection) / float(union)


def groupJaccard():
    # 1 load keyword curves grouped results
    with open('/Users/white/Documents/Limit-Paper/postgresql/k10/keyword_curves_grouped.csv') as f1:
        reader = csv.reader(f1)
        keywordGroups = list(reader)
    with open('/Users/white/Documents/Limit-Paper/postgresql/k10/keyword_curves_grouped_sample.csv') as f2:
        reader = csv.reader(f2)
        keywordGroups_sample = list(reader)

    groupKeywords = {}
    groupKeywords_sample = {}

    for kg in keywordGroups:
        if kg[21] in groupKeywords.keys():
            groupKeywords[kg[21]].append(kg[0])
        else:
            groupKeywords[kg[21]] = [kg[0]]

    for kgs in keywordGroups_sample:
        if kgs[21] in groupKeywords_sample.keys():
            groupKeywords_sample[kgs[21]].append(kgs[0])
        else:
            groupKeywords_sample[kgs[21]] = [kgs[0]]

    with open('groups_jaccard.csv', 'w') as csvFile:
        csvWriter = csv.writer(csvFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for g1 in groupKeywords.keys():
            for g2 in groupKeywords_sample.keys():
                row = [g1, g2]
                row.extend(jaccardSimilarity(groupKeywords[g1], groupKeywords_sample[g2]))
                csvWriter.writerow(row)


def verifyOrderBetweenSampleAndOriginal(p_keyword):
    l_original = db.GetID(tableName, p_keyword, -1)
    l_sample = db.GetID(tableName + '_sample', p_keyword, -1)

    l_original = list(map(lambda record: record[0], l_original))
    l_sample = list(map(lambda record: record[0], l_sample))

    # l_max_index = 0
    # for l_id in l_sample:
    #     l_index = l_original.index(l_id)
    #     if l_index <= l_max_index:
    #         print "Found this id:", l_id, "disordered... index =", l_index
    #         return
    #     else:
    #         l_max_index = l_index

    j = 0
    for i in range(0, len(l_sample), 1):
        while l_sample[i] != l_original[j]:
            j += 1
            if j == len(l_original):
                rj = l_original.index(l_sample[i])
                print "Element:", l_sample[i], "in sample the", i, "th place is in original the", rj, "th place."
                rj_1 = l_original.index(l_sample[i-1])
                print "But element:", l_sample[i-1], "in sample the", i-1, "th place is in original the", rj_1, "th place"
                return False

    print "All records in sample follow the same order as in original data set"
    return True


###########################################################
#  Run Script
###########################################################

# print '================================================='
# print '  ' + database + '  Experiments - 4.2 Keywords Grouping'
# print 'Ground Truth : Group by curves clustering by K-Means'
# print '================================================='
# print 'table:', tableName
# print 'frequency range:[', min_freq, ',', max_freq, ']'
# print 'K:', K
# print '================================================='
# start = time.time()
# groupByCurves(min_freq, max_freq, K)
# end = time.time()
# print '-------------------------------------------------'
# print 'Ground Truth is done!'
# print 'Total time:', end - start

# print '================================================='
# print '  ' + database + '  Experiments - 4.2 Keywords Grouping'
# print 'Approach 1: Group by frequency natural boundaries'
# print '================================================='
# print 'table:', tableName
# print 'frequency range:[', min_freq, ',', max_freq, ']'
# print 'Unit frequency:', unit_freq
# print 'Max density:', max_density
# print '================================================='
# start = time.time()
# numOfGroups, computeTime, queryTime, plotTime = groupByFrequency(min_freq, max_freq, unit_freq, max_density)
# end = time.time()
# print '-------------------------------------------------'
# print 'Approach 1 is done!'
# print 'Total number of groups:', numOfGroups
# print 'Time of computing:', computeTime
# print 'Time of querying:', queryTime
# print 'Time of plotting:', plotTime
# print 'Total time:', end - start
#
# print '================================================='
# print '  ' + database + '  Experiments - 4.2 Keywords Grouping'
# print 'Approach 2: Group by frequency clustering by K-Means'
# print '================================================='
# print 'table:', tableName
# print 'frequency range:[', min_freq, ',', max_freq, ']'
# print 'K:', K
# print '================================================='
# start = time.time()
# numOfGroups, computeTime, queryTime, plotTime = groupByFrequencyKMeans(K)
# end = time.time()
# print '-------------------------------------------------'
# print 'Approach 2 is done!'
# print 'Total number of groups:', numOfGroups
# print 'Time of computing:', computeTime
# print 'Time of querying:', queryTime
# print 'Time of plotting:', plotTime
# print 'Total time:', end - start
#
# print '================================================='
# print '  ' + database + '  Experiments - 4.2 Keywords Grouping'
# print 'Approach 3: Group by density and skewness clustering by K-Means'
# print '================================================='
# print 'table:', tableName
# print 'frequency range:[', min_freq, ',', max_freq, ']'
# print 'K:', K
# print '================================================='
# start = time.time()
# groupByDensityAndSkewnessKMeans(min_freq, max_freq, K)
# end = time.time()
# print '-------------------------------------------------'
# print 'Approach 3 is done!'
# print 'Total number of groups:', K
# print 'Total time:', end - start

# print '================================================='
# print '  ' + database + '  Experiments - 4.2 Keywords Grouping'
# print 'Approach 4: Group by frequency and density and skewness clustering by K-Means'
# print '================================================='
# print 'table:', tableName
# print 'frequency range:[', min_freq, ',', max_freq, ']'
# print 'K:', K
# print '================================================='
# start = time.time()
# groupByFrequencyAndDensityAndSkewnessKMeans(min_freq, max_freq, K)
# end = time.time()
# print '-------------------------------------------------'
# print 'Approach 4 is done!'
# print 'Total number of groups:', K
# print 'Total time:', end - start
#
# print '================================================='
# print '  ' + database + '  Experiments - 4.2 Keywords Grouping'
# print 'Approach 5: Group by cell length and density and skewness clustering by K-Means'
# print '================================================='
# print 'table:', tableName
# print 'frequency range:[', min_freq, ',', max_freq, ']'
# print 'K:', K
# print '================================================='
# start = time.time()
# groupByCellLenAndDensityAndSkewnessKMeans(min_freq, max_freq, K)
# end = time.time()
# print '-------------------------------------------------'
# print 'Approach 5 is done!'
# print 'Total number of groups:', K
# print 'Total time:', end - start

# print '================================================='
# print '  ' + database + '  Experiments - 4.2 Keywords Grouping'
# print 'Approach 6: Group by frequency and cell length and density and skewness clustering by K-Means'
# print '================================================='
# print 'table:', tableName
# print 'frequency range:[', min_freq, ',', max_freq, ']'
# print 'K:', K
# print '================================================='
# start = time.time()
# groupByFreqAndCellLenAndDensityAndSkewnessKMeans(min_freq, max_freq, K)
# end = time.time()
# print '-------------------------------------------------'
# print 'Approach 6 is done!'
# print 'Total number of groups:', K
# print 'Total time:', end - start

# verifyOrderBetweenSampleAndOriginal('recommend')
# verifyOrderBetweenSampleAndOriginal('interest')
# verifyOrderBetweenSampleAndOriginal('retail')
# verifyOrderBetweenSampleAndOriginal('day')
# verifyOrderBetweenSampleAndOriginal('need')
# verifyOrderBetweenSampleAndOriginal('weekend')

print '================================================='
print '  ' + database + '  Experiments - 4.2 Keywords Grouping'
print 'Approach 7 : Group by curves from sample data set clustering by K-Means'
print '================================================='
print 'table:', tableName
print 'frequency range:[', min_freq, ',', max_freq, ']'
print 'curves range:[', start_pk, ',', end_pk, ']'
print 'K:', K
print '================================================='
start = time.time()
groupBySampleCurves(min_freq, max_freq, start_pk, end_pk, K)
end = time.time()
print '-------------------------------------------------'
print 'Approach 7 is done!'
print 'Total time:', end - start

# print '================================================='
# print '  ' + database + '  Experiments - 4.2 Keywords Grouping'
# print 'Approach 8 : Group by curves from sample data set clustering by K-Means but bounded by frequency ranges'
# print '================================================='
# print 'table:', tableName
# print 'frequency range:[', min_freq, ',', max_freq, ']'
# print 'curves range:[', start_pk, ',', end_pk, ']'
# print 'curves density:', curve_density
# print '================================================='
# start = time.time()
# # Divide the frequency range into ranges from min to max with step increasing exponentially:
# # min - min * freq_step^2
# # e.g. freq_step = 2:
# # 5000 - 5000 * 2
# # 10000 - 10000 * 4
# # 40000 - 20000 * 16
# # ... ...
# freq_step = 2
# i_min_freq = min_freq
# i_max_freq = min_freq
# while i_min_freq < max_freq:
#     i_min_freq = i_max_freq
#     i_max_freq = min(i_min_freq * freq_step, max_freq)
#     freq_step = freq_step * freq_step
#     i_num_of_keywords = getNumOfKeywords(i_min_freq, i_max_freq)
#     if i_num_of_keywords > curve_density:
#         i_k = int(i_num_of_keywords / curve_density)
#     elif i_num_of_keywords > 3:
#         i_k = 3
#     elif i_num_of_keywords > 0:
#         i_k = 1
#     else:
#         continue
#     groupBySampleCurves(i_min_freq, i_max_freq, start_pk, end_pk, i_k)
# end = time.time()
# print '-------------------------------------------------'
# print 'Approach 8 is done!'
# print 'Total time:', end - start

# print '================================================='
# print '  ' + database + '  Experiments - 4.2 Keywords Grouping'
# print 'Approach 9 : Group by k values from sample data set clustering by K-Means'
# print '================================================='
# print 'table:', tableName
# print 'frequency range:[', min_freq, ',', max_freq, ']'
# print 'K:', K
# print '================================================='
# start = time.time()
# groupBySampleKValues(min_freq, max_freq, K)
# end = time.time()
# print '-------------------------------------------------'
# print 'Approach 9 is done!'
# print 'Total time:', end - start

db.close()

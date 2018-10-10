from sklearn.cluster import KMeans
import csv
import os


# get the curves for keywords in given frequency range generated from p_table
# p_db: handle of database
# p_table: the table from which the curves are generated
# p_min_freq, p_max_freq: frequency range of keywords that we want to get curves for
# return: a list of [word, q(5%), q(10%), ..., q(95%)]
def getCurvesOfKeywords(p_db, p_table, p_min_freq, p_max_freq):
    results = p_db.queryCurves(p_table, p_min_freq, p_max_freq)
    return results


def tagLabels(p_curves, p_labels):
    for i in range(0, len(p_curves), 1):
        p_curves[i].append(p_labels[i])
    return p_curves


# cluster the keywords by curves using k-means
# p_db: handle of database
# p_table: the table from which the curves are generated
# p_min_freq, p_max_freq: frequency range of keywords to be clustered
# p_k: the k value for k-means algorithm, default 10
# return: the curves of keywords labeled by clustering results
#         a list of [word, q(5%), q(10%), ..., q(95%), cluster_label]
def clusterByCurves(p_db, p_table, p_min_freq, p_max_freq, p_k=10):
    # get all curves of keywords
    l_curves = getCurvesOfKeywords(p_db, p_table, p_min_freq, p_max_freq)
    # get rid of word field
    l_vector_curves = map(lambda cur: cur[1:len(l_curves)-1], l_curves)

    # 1. K-Means
    l_km = KMeans(n_clusters=p_k)
    l_km.fit(l_vector_curves)

    # 2. write the labeled curves to csv file
    # label K-Means
    l_labeled_curves = tagLabels(l_curves, l_km.labels_)

    return l_labeled_curves


# write the labeled keywords in labeled curves into a csv file
# p_table: the table from which the curves are generated
# p_labeled_curves: the curves labeled by the clusterByCurves function in this file
# p_csvFilePath: absolute file path for the target csv file to write to
# p_k: the k value for k-means algorithm, default 10
# csv file name: {p_table}_{p_min_freq}_{p_max_freq}_{p_k}_word_clusters.csv
# csv file format: [{p_table}, {p_min_freq}, {p_max_freq}, {p_k}, keyword, cluster_label]
def writeLabeledKeywordsToCSV(p_table, p_min_freq, p_max_freq, p_labeled_curves, p_csvFilePath, p_k=10):
    l_csvFile = p_csvFilePath + '/' + p_table + '_' + str(p_min_freq) + '_' + str(p_max_freq) + \
                '_' + str(p_k) + '_word_clusters.csv'
    # only keep the word and cluster_label for each line of p_labeled_curves
    l_labeled_keywords = map(lambda cur: [cur[0], cur[len(cur)-1]], p_labeled_curves)
    with open(l_csvFile, 'w') as csvFile:
        csvWriter = csv.writer(csvFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for labeled_keyword in l_labeled_keywords:
            line = [p_table, p_min_freq, p_max_freq, p_k]
            line.extend(labeled_keyword)
            csvWriter.writerow(line)
    return l_csvFile


# load the clustered keywords csv file into database
# p_db: database handle
# p_csvFile: absolute path for the csv file returned by the writeLabeledKeywordsToCSV function in this file
def loadCurvesCSVToDB(p_db, p_csvFile):
    return p_db.loadCSVToTable(os.path.abspath(p_csvFile), 'word_clusters')


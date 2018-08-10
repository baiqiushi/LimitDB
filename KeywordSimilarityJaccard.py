import csv
import CurveGenerator
import Conf
import DatabaseFactory
import numpy as np
import KeywordsUtil


database = Conf.DATABASE
tableName = Conf.TABLE


# Keywords frequency range
min_freq = 5000
max_freq = 4000000

db = DatabaseFactory.getDatabase(database)


def getPerfectImage(p_keyword):
    ar = np.array(db.GetCoordinate(tableName, p_keyword, -1))
    if len(ar) == 0:
        return []
    # perfect image
    H = CurveGenerator.hashByNumpy(ar)
    return H.ravel()


def collectPerfectImages():

    keywords = KeywordsUtil.pickAllInFrequencyRange(min_freq, max_freq)

    csvFileName = 'keyword_perfect_images.csv'

    with open(csvFileName, 'w') as csvFile:
        csvWriter = csv.writer(csvFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for keyword in keywords:
            img = getPerfectImage(keyword[0])
            np.append(img, keyword[0])
            csvWriter.writerow(img)


def jaccardSimilarity(list1, list2):
    intersection = len(list(set(list1).intersection(list2)))
    # print(list(set(list1).intersection(list2)))
    # print "intersection = ", intersection
    union = (len(list1) + len(list2)) - intersection
    # print "union = ", union
    return float(intersection) / float(union)


# return a dictionary
# { 0: {'job': [id0, id1, id2, ...],
#       'latest': [id0, id3, id4, ...],
#        ...},
#   1: {...},
#   ...
# }
# p_k - number of groups totally
# p_numPerGroup - number of keywords randomly picked for each group
def collectRecordsListOfGroups(p_k, p_numPerGroup):

    result = {}

    # Traverse the group labels
    for i in range(0, p_k, 1):
        # For each group, randomly pick p_numPerGroup keywords
        keywords = KeywordsUtil.randomPickInCurveGroup(i, p_numPerGroup)
        if len(keywords) < p_numPerGroup:
            continue
        result[i] = {}
        # For each keyword, get all the records ID list
        for keyword in keywords:
            ids = db.GetID(tableName, keyword, -1)
            result[i][keyword] = ids

    return result


def collectJaccardSimilarities(p_k, p_numPerGroup):
    groupsOfKeywordsIDs = collectRecordsListOfGroups(p_k, p_numPerGroup)

    # 1. Jaccard similarities inside groups
    csvFileName = 'in_group_jaccard.csv'
    inGroupJaccard = []
    for group in groupsOfKeywordsIDs:

        groupJaccard = [group]

        keywordsIDs = groupsOfKeywordsIDs[group]
        keywords = keywordsIDs.keys()

        groupJaccard.extend(list(keywords))

        for i in range(0, len(keywords), 1):
            for j in range(i + 1, len(keywords), 1):
                js = jaccardSimilarity(keywordsIDs[keywords[i]], keywordsIDs[keywords[j]])
                groupJaccard.append(js)

        inGroupJaccard.append(groupJaccard)

    with open(csvFileName, 'w') as csvFile:
        csvWriter = csv.writer(csvFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for gj in inGroupJaccard:
            csvWriter.writerow(gj)

    # 2. Jaccard similarities between groups
    csvFileName = 'out_group_jaccard.csv'
    outGroupJaccard = []
    groups = groupsOfKeywordsIDs.keys()
    for i in range(0, len(groups), 1):
        for j in range(i + 1, len(groups), 1):
            group1 = groupsOfKeywordsIDs[groups[i]]
            group2 = groupsOfKeywordsIDs[groups[j]]

            groupJaccard = [groups[i], groups[j]]

            keywords1 = group1.keys()
            keywords2 = group2.keys()

            groupJaccard.extend(keywords1)
            groupJaccard.extend(keywords2)

            for keyword1 in keywords1:
                for keyword2 in keywords2:
                    js = jaccardSimilarity(group1[keyword1], group2[keyword2])
                    groupJaccard.append(js)

            outGroupJaccard.append(groupJaccard)

    with open(csvFileName, 'w') as csvFile:
        csvWriter = csv.writer(csvFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for gj in outGroupJaccard:
            csvWriter.writerow(gj)


def test_jaccardSimilarity():
    l1 = [825495396495536128, 824943636106375169, 853367994575204354]
    l2 = [825495396495536128, 824943636106375169, 839250930004537347]
    print jaccardSimilarity(l1, l2)


def test_jaccardSimilarity2():
    fire = db.GetID(tableName, 'fire', -1)
    chicago = db.GetID(tableName, 'chicago', -1)
    print "length of fire = ", len(fire)
    print "length of chicago = ", len(chicago)
    print jaccardSimilarity(fire, chicago)


collectJaccardSimilarities(2, 3)


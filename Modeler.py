import Conf
import DatabaseFactory
import numpy as np
import QualityUtil

###########################################################
#   Configurations
###########################################################
database = Conf.DATABASE
tableName = Conf.TABLE

db = DatabaseFactory.getDatabase(database)


# Given a keyword, use binary search to find the limit k value for target quality with given r value
# p_keyword - keyword
# p_quality - target quality value, float in [0, 1]
# p_r - r value for hybrid approach with condition random() < r in the query, float in [0, 1]
# return [limit k value, limit k ratio] with which we can get target quality
#        [-1, -1] if with maximum k value, we still cannot get target quality
def findKOfQuality(p_keyword, p_quality, p_r, p_totalCoordinates):

    # 1. Get perfect image if not indicated by argument
    if p_totalCoordinates:
        totalCoordinates = p_totalCoordinates
    else:
        totalCoordinates = db.GetCoordinate(tableName, p_keyword, -1)

    # 2. If max possible image with given r value is smaller than p_quality, return [-1, -1]
    maxCoordinates = db.GetCoordinateHybrid(tableName, p_keyword, p_r, int(len(totalCoordinates) * p_r))
    maxQuality = QualityUtil.phQualityOfCoordinates(totalCoordinates, maxCoordinates)
    if maxQuality < p_quality:
        return [-1, -1]

    # 3. Binary search to find the k value for target quality
    i = 0.0
    low = 0.0
    high = 100.0 * p_r
    similarity = 0.0
    iterTimes = 0
    while (similarity < p_quality or similarity > p_quality + 0.01) and iterTimes < 10:
        # binary search for the target k for target quality
        if similarity < p_quality:
            low = i
            i = (high + i) / 2
        elif similarity > p_quality + 0.01:
            high = i
            i = (i + low) / 2
        k = int(i * len(totalCoordinates) / 100)
        i_coordinates = db.GetCoordinateHybrid(tableName, p_keyword, p_r, k)
        similarity = QualityUtil.phQualityOfCoordinates(totalCoordinates, i_coordinates)
        iterTimes += 1
    return k, i


# Given a keyword, and possible r values in an array p_rs,
# for each r value in p_rs, find the exact k value that can make the hybrid query results
# meet the target quality requirement.
# p_keyword - keyword
# p_quality - target quality value, float in [0, 1]
# p_rs - array of possible r values, [r0, r1, r2, ..., r10], ri is float in [0, 1]
# return [[r0, k0], [r1, k1], ..., [rx, kx]] a list of [r, k] pairs that can satisfy this
#        p_quality requirement
def findKROfQuality(p_keyword, p_quality, p_rs):

    # 1. Get perfect image which can be reused for each call of findKOfQuality()
    totalCoordinates = db.GetCoordinate(tableName, p_keyword, -1)

    result = []

    for r in p_rs:
        k = findKOfQuality(p_keyword, p_quality, r, totalCoordinates)
        if k[0] > 0:
            result.append([r, k])

    return result

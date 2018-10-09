import numpy as np

# Resolution of image
res_x = 1920/4
res_y = 1080/4


def printInfo(p_x_scale=1, p_y_scale=1):
    print 'quality function: Boolean Perceptual Hash'
    print 'resolution:', int(res_x/p_x_scale), 'x', int(res_y/p_y_scale)


def coordinatesToImage(ar, p_res_x=res_x, p_res_y=res_y, r=((-170, -60), (15, 70))):
    H, x, y = np.histogram2d(ar[:, 0], ar[:, 1], bins=(p_res_x, p_res_y), range=r)
    return H


# Perceptual Hash Quality of K percentage limit image corresponding to perfect image
# p_totalCoordinates - list of all coordinates of perfect image
# p_k_percentage - percentage of limit k (e.g. 10 - 10%), this function will translate k% into actual k value
# return similarity between k percentage image and perfect image, normalized to [0, 1]
def phQualityOfKPercentage(p_totalCoordinates, p_k_percentage, p_x_scale=1, p_y_scale=1):
    totalCoordinates = np.array(p_totalCoordinates)
    # ground truth perfect image
    perfectImage = coordinatesToImage(totalCoordinates, int(res_x/p_x_scale), int(res_y/p_y_scale))
    # mimic limit k behavior of DB
    k = int(p_k_percentage * len(totalCoordinates) / 100)
    # limit k percentage of coordinates image
    kPercentageImage = coordinatesToImage(totalCoordinates[:k], int(res_x/p_x_scale), int(res_y/p_y_scale))
    # calculate similarity
    perfectNumOfCells = np.count_nonzero(perfectImage)
    kPercentNumOfCells = np.count_nonzero(kPercentageImage)
    similarity = float(kPercentNumOfCells) / float(perfectNumOfCells)

    return similarity


def phQualityOfCoordinates(p_totalCoordinates, p_coordinates, p_x_scale=1, p_y_scale=1):
    # ground truth perfect image
    totalCoordinates = np.array(p_totalCoordinates)
    perfectImage = coordinatesToImage(totalCoordinates, int(res_x/p_x_scale), int(res_y/p_y_scale))
    # target image
    targetCoordinates = np.array(p_coordinates)
    targetImage = coordinatesToImage(targetCoordinates, int(res_x / p_x_scale), int(res_y / p_y_scale))
    # calculate similarity
    perfectNumOfCells = np.count_nonzero(perfectImage)
    targetNumOfCells = np.count_nonzero(targetImage)
    similarity = float(targetNumOfCells) / float(perfectNumOfCells)

    return similarity


# Use binary search to find the limit k value for target quality
# p_totalCoordinates - list of all coordinates of perfect image
# p_quality - target quality value, float in [0, 1]
# return [limit k value, limit k ratio] with which we can get target quality
def findKOfQuality(p_totalCoordinates, p_quality, p_x_scale=1, p_y_scale=1):
    totalCoordinates = np.array(p_totalCoordinates)
    # ground truth perfect image
    perfectImage = coordinatesToImage(totalCoordinates, int(res_x/p_x_scale), int(res_y/p_y_scale))
    perfectNumOfCells = np.count_nonzero(perfectImage)
    i = 0.0
    low = 0.0
    high = 100.0
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
        sampleImage = coordinatesToImage(totalCoordinates[:k], int(res_x/p_x_scale), int(res_y/p_y_scale))
        sampleNumOfCells = np.count_nonzero(sampleImage)
        similarity = float(sampleNumOfCells) / perfectNumOfCells
        iterTimes += 1
    return k, i

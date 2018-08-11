import numpy as np

# Resolution of image
res_x = 1920/4
res_y = 1080/4


def printInfo():
    print 'quality function: Boolean Perceptual Hash'
    print 'resolution:', res_x, 'x', res_y


def coordinatesToImage(ar, r=((-170, -60), (15, 70))):
    H, x, y = np.histogram2d(ar[:, 0], ar[:, 1], bins=(res_x, res_y), range=r)
    return H


# Perceptual Hash Quality of K percentage limit image corresponding to perfect image
# p_totalCoordinates - list of all coordinates of perfect image
# p_k_percentage - percentage of limit k (e.g. 10 - 10%), this function will translate k% into actual k value
# return similarity between k percentage image and perfect image, normalized to [0, 1]
def phQualityOfKPercentage(p_totalCoordinates, p_k_percentage):
    totalCoordinates = np.array(p_totalCoordinates)
    # ground truth perfect image
    perfectImage = coordinatesToImage(totalCoordinates)
    # mimic limit k behavior of DB
    k = int(p_k_percentage * len(totalCoordinates) / 100)
    # limit k percentage of coordinates image
    kPercentageImage = coordinatesToImage(totalCoordinates[:k])
    # calculate similarity
    perfectNumOfCells = np.count_nonzero(perfectImage)
    kPercentNumOfCells = np.count_nonzero(kPercentageImage)
    similarity = float(kPercentNumOfCells) / float(perfectNumOfCells)

    return similarity

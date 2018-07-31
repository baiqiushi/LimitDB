import matplotlib.pyplot as plt
import cv2 as cv  # pip install opencv-python


def DrawImage(matrix, fn):
    x = []
    y = []
    for r in matrix:
        if -60.0 >= r[0] >= -170.0 and 70.0 >= r[1] >= 15.0:
            x.append(r[0])
            y.append(r[1])
    # print fn,len(x),len(y)
    plt.scatter(x, y, s=1, c="b", marker='.')
    # plt.yticks([xt for xt in range(15,70,5)])
    # plt.xticks([yt for yt in range(-170,-60,10)])
    plt.ylim(15, 70)
    plt.xlim(-170, -60)
    plt.savefig(fn, bbox_inches='tight', dpi=350)
    plt.close()


def GetGrayImage(p_file):
    image = cv.imread(p_file)
    image = cv.cvtColor(image, cv.COLOR_RGB2GRAY)
    return image


def GetSimilarityFromImages(p1, p2):
    one = 0.0
    diff = 0.0
    for i in range(55, 1344):
        for j in range(133, 1864):
            if p1[i][j] > 230:
                a = 1
            else:
                a = 0
            if p2[i][j] > 230:
                b = 1
            else:
                b = 0
            if a == b == 1:
                one +=1
            else:
                if a != b:
                    diff += 1
    similarity = 1-diff/((1344-55)*(1864-133)-one)
    return similarity

import numpy as np

# This function convert from a single channel image to a binary image matrix.
def createBinaryImage(oldImage, min, max):
    oldImageWidth = len(oldImage)
    oldImageHeight = len(oldImage[0])
    binaryImageMatrix = np.zeros((oldImageWidth, oldImageHeight), dtype=np.uint8)
    for x in range(oldImageWidth):
        for y in range(oldImageHeight):
                if (oldImage[x][y] > min) & (oldImage[x][y] <= max):
                    binaryImageMatrix[x][y] = 255
    return binaryImageMatrix

def inRange(pic, upper=(1,1,1), lower=(0,0,0)):
    outImg = np.zeros((pic.shape[0],pic.shape[1]), dtype=np.uint8)
    for i in range(pic.shape[0]):
        for j in range(pic.shape[1]):
            cur = pic[i][j]
            if cur[0] >= lower[0] and cur[1] >= lower[1] and cur[2] >= lower[2] and cur[0] <= upper[0] and cur[1] <= upper[1] and cur[2] <= upper[2]:
                outImg[i][j] = 255
    return outImg
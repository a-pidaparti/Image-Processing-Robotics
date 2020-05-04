import numpy as np
import json
import math
from blob import Blob
import matplotlib.pyplot as plot
import convertToHSV as toHSV
import createBinaryImage as bi
import cv2
from operator import itemgetter

def isEdge(image, x, y):
    if ((y-1) < 0) | ((x-1) < 0) | ((y+1) >= len(image[0])) | ((x+1) >= len(image)):
        return True
    up = image[x][y-1]
    down = image[x][y+1]
    left = image[x-1][y]
    right = image[x+1][y]
    upLeft = image[x-1][y-1]
    upRight = image[x+1][y-1]
    downLeft = image[x-1][y+1]
    downRight = image[x+1][y+1]
    if (up == 0) | (down == 0) | (right == 0) | (left == 0) | (downLeft == 0) | (downRight == 0) | (upRight == 0) | (upLeft == 0):
        return True
    else:
        return False
                          
# This function crawls a binary image matrix from left to right and top to bottom looking
# returns a list of blob objects (see "blob.py")
def blobDetect(pic, min, max, channel):
    hsvInt = np.zeros((len(pic),len(pic[0]),len(pic[0][0])), dtype=np.uint8)
    hsv = toHSV.convertToHSV(pic)
    binaryImage = bi.createBinaryImage(hsv[:,:,channel],min,max)
    binaryImageWidth = len(binaryImage)
    binaryImageHeight = len(binaryImage[0])
    alreadyDetected = []
    blobList = []
    #(binaryImage)
    for y in range(binaryImageHeight):
        for x in range(binaryImageWidth):
            if binaryImage[x][y] > 0:
                coordList = []
                firstRun = True
                i = x
                j = y
                leftMostX = x;
                rightMostX = x;
                topMostY = y;
                bottomMostY = y;
                notAppendedCount = 0
                #print("started while loop")
                while (i < (binaryImageWidth-1)) & (j < (binaryImageHeight-1)):
                    # check pixel above
                    if (binaryImage[i][j-1] > 0) & (([i,j-1] in coordList) == False) & isEdge(binaryImage, i, j-1):
                        j = j - 1
                        if j < topMostY:
                            topMostY = j
                        #print("i, j: ", i, j)
                        notAppendedCount = 0
                        coordList.append([i,j])
                    # check pixel right
                    elif (binaryImage[i+1][j] > 0) & (([i+1,j] in coordList) == False) & isEdge(binaryImage, i+1, j):
                        i = i + 1
                        if i > rightMostX:
                            rightMostX = i
                        # print("i, j: ", i, j)
                        notAppendedCount = 0
                        coordList.append([i,j])
                    # check pixel below
                    elif (binaryImage[i][j+1] > 0) & (([i,j+1] in coordList) == False) & isEdge(binaryImage, i, j+1):
                        j = j + 1
                        if j > bottomMostY:
                            bottomMostY = j
                        # print("i, j: ", i, j)
                        notAppendedCount = 0
                        coordList.append([i,j])
                    # check pixel left
                    elif (binaryImage[i-1][j] > 0) & (([i-1,j] in coordList) == False) & isEdge(binaryImage, i-1, j):
                        i = i - 1
                        if i < leftMostX:
                            leftMostX = i
                        # print("i, j: ", i, j)
                        notAppendedCount = 0
                        coordList.append([i,j])
                    # check pixel above
                    elif (binaryImage[i][j-1] > 0) & isEdge(binaryImage, i, j-1):
                        j = j - 1
                        notAppendedCount = notAppendedCount + 1
                        # print("NOT APPENDED: i, j: ", i, j)
                    # check pixel right
                    elif (binaryImage[i+1][j] > 0) & isEdge(binaryImage, i+1, j):
                        i = i + 1
                        notAppendedCount = notAppendedCount + 1
                        # print("NOT APPENDED: i, j: ", i, j)
                    # check pixel below
                    elif (binaryImage[i][j+1] > 0) & isEdge(binaryImage, i, j+1):
                        j = j + 1
                        notAppendedCount = notAppendedCount + 1
                        # print("NOT APPENDED: i, j: ", i, j)
                    # check pixel left
                    elif (binaryImage[i-1][j] > 0) & isEdge(binaryImage, i-1, j):
                        i = i - 1
                        notAppendedCount = notAppendedCount + 1
                        # print("NOT APPENDED: i, j: ", i, j)
                    else:
                        a=  5
                        #print("NOWHERE TO GO: ", i, j)
                    if ((i == x) & (j == y)) | (notAppendedCount > 4):
                        for [xa, ya] in coordList:
                            binaryImage[xa][ya] = 0
                        break
                        
                # draw a black rectangle around the detected region, (ie: remove all True pixels
                # from that region.)  This prevents an object from being detected multiple times.
                for a in range(leftMostX, rightMostX):
                    for b in range(topMostY, bottomMostY):
                        binaryImage[a][b] = 0;
                # If the blob outline was within image bounds and the outline length
                # was longer than 64 (used to filter out objects that are too small) append a new Blob object
                if (i < (binaryImageWidth-1)) & (j < (binaryImageHeight-1)) & (len(coordList) > 32):
                    #print("appended blob")
                    blobList.append(Blob(coordList, pic))
                    if len(blobList[-1].get_corners()) < 4:
                        blobList = blobList[:-1]
                        print("shape discarded")
                    else:
                        blobList[-1].order_corners(blobList[-1].get_corners())
    return blobList

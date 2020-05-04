# Written By: Morgan Kuphal (kupha014@umn.edu) 4/23/2020
import numpy as np
import math

# This function is used to ensure the frame of the image is orthogonal to the real world frame
# by rotating the image about its z-axis located in the center of the image. The real world frame
# of reference is formed by the lines pointing from the upper left corner of the upper left 
# calibration square to the upper right corner of the upper right calibration square (x-axis) and
# the bottom left corner of the bottomm left calibration square (y-axis)
def correctImageRotation(oldImage, leftCalPointX, leftCalPointY, rightCalPointX, rightCalPointY):
    oldImageWidth = len(oldImage)
    oldImageHeight = len(oldImage[0])
    numChannels = len(oldImage[0][0])
    paddedImageDimensions = math.ceil(math.sqrt(len(oldImage[0])**2 + len(oldImage[0]**2)))
    newImageCenter = math.floor(paddedImageDimensions/2)
    # t = theta (amount of rotation needed to correct the image)
    t = math.atan((leftCalPointY - rightCalPointY)/(rightCalPointX - leftCalPointX))
    # create padded image to avoid overstepping array bounds when performing rotation
    imageLeftPadding = math.floor((paddedImageDimensions - oldImageWidth) / 2)
    imageTopPadding = math.floor((paddedImageDimensions - oldImageHeight) / 2)
    newImage = np.zeros((paddedImageDimensions, paddedImageDimensions, numChannels))
    for x in range(oldImageWidth):
        for y in range(oldImageHeight):
            # the same transformation matrix used in robotics can be applied to pixels in an image
            # to achieve translation or rotation about any axis (although this matrix only deals with x & y axes)
            T = [[math.cos(t), -math.sin(t), -newImageCenter], [math.sin(t), math.cos(t), -newImageCenter], [0, 0, 1]]
            result = T * [ x, y, 1]
            newX = result[0]
            newY = result[1]
            for z in range(numChannels):
                # pixel transform matrix
                newImage[newX + newImageCenter][newY + newImageCenter][z] = oldImage[x][y][z]
    # crop so that no padding pixels remain
    newImageWidth = math.floor(oldImageWidth * math.cos(t))
    widthSplit = oldImageWidth - math.ceil(newImageWidth / 2)
    newImageHeight = math.floor(oldImageHeight * math.sin(t))
    heightSplit = oldImageHeight - math.ceil(newImageHeight / 2)
    newImage = newImage[imageLeftPadding+widthSplit:imageLeftPadding+newImageWidth+widthSplit-1][imageTopPadding+heightSplit:imageTopPadding+newImageHeight+heightSplit-1][:]
    return newImage

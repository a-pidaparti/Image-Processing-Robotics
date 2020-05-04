import numpy as np

def convertToHSV(oldImage):
    oldImageWidth = len(oldImage)
    oldImageHeight = len(oldImage[0])
    numChannels = len(oldImage[0][0])
    newImage = np.zeros((oldImageWidth, oldImageHeight, numChannels))
    for x in range(oldImageWidth):
        for y in range(oldImageHeight):
            max = oldImage[x][y][0]
            min = oldImage[x][y][0]
            z = numChannels-1;
            while z > 0:
                if oldImage[x][y][z] > max:
                    max = oldImage[x][y][z]
                if oldImage[x][y][z] < min:
                    min = oldImage[x][y][z]
                z = z - 1;
            v = max / 255;
            delta = max - min;
            if delta == 0:
                h = 0;
                s = 0;
            else:
                s = delta / max;
                if (oldImage[x][y][0] / 255) == v:
                    h = ((int(oldImage[x][y][1]) - int(oldImage[x][y][2])) / delta) % 6
                elif (oldImage[x][y][1] / 255) == v:
                    h = 2 + ((int(oldImage[x][y][2]) - int(oldImage[x][y][0])) / delta)
                else:
                    h = 4 + ((int(oldImage[x][y][0]) - int(oldImage[x][y][1])) / delta)
                h = h / 6
            newImage[x][y][:] = [ h, s, v ]
    return newImage
from operator import itemgetter
import numpy as np
from shapes import Shape
import cv2
class Blob(Shape):
    def __init__(self, perimeterCoordinates, pic):
        # list of x,y coordinates which make up the outline of a blob
        # self.ignore = perimeterCoordinates < 4
        self.center = (-1,-1)
        self.orientation = -1
        self.blobCoordinates = []
        perimeterCoordinates = sorted(perimeterCoordinates, key=itemgetter(1))
        self.perimeter = np.array(perimeterCoordinates)
        for i in range(len(self.perimeter)):
            self.perimeter[i][0],self.perimeter[i][1] = self.perimeter[i][1],self.perimeter[i][0]
        Shape.__init__(self, self.perimeter, pic)


        #print(perimeterCoordinates)
        alreadyProcessedRow = []
        for i in range(len(perimeterCoordinates)):
            y = perimeterCoordinates[i][1]
            if (y in alreadyProcessedRow) == False:
                xmax = perimeterCoordinates[i][0]
                xmin = perimeterCoordinates[i][0]
                alreadyProcessedRow.append(y)
                j = i
                while (perimeterCoordinates[j][1] == y):
                    if perimeterCoordinates[j][0] < xmin:
                        xmin = perimeterCoordinates[j][0]
                    if perimeterCoordinates[j][0] > xmax:
                        xmax = perimeterCoordinates[j][0]
                    j = j + 1
                    if j == len(perimeterCoordinates):
                        break
                for a in range(xmin, xmax):
                    self.blobCoordinates.append([a, y])

    # returns a list of all coordinates which make up the blob
    def getCoordinates(self):
        return self.blobCoordinates

    def getOutline(self):
        return self.outline

    def __cmp__(self, other):
        return cv2.contourArea(self.perimeter) > cv2.contourArea(other.perimeter)
    def __gt__(self, other):
        return cv2.contourArea(self.perimeter) > cv2.contourArea(other.perimeter)
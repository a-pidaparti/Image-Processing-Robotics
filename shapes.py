import cv2
import numpy as np
import math
import goodFeaturesToTrack as gftt
import convertToHSV as toHSV
import createBinaryImage as bi


def boundingRect(contour):
    lowestX = float('inf')
    lowestY = float('inf')
    highestX = -1
    highestY = -1
    for i in contour:
        x,y = i
        if x < lowestX:
            lowestX = x
        if x > highestX:
            highestX = x
        if y < lowestY:
            lowestY = y
        if y > highestY:
            highestY = y
    return (lowestX, lowestY, highestX - lowestX, highestY - lowestY)

def getTopRight(seg1, seg2):
    pt1,pt2 = seg1
    pt3, pt4 = seg2
    if pt1[1] > pt2[1]:
        upper1 = pt1
    else:
        upper1 = pt2

    if pt3[1] > pt4[1]:
        upper2 = pt3
    else:
        upper2 = pt4

    if upper1[0] > upper2[0]:
        return upper1
    return upper2

def getTopLeft(seg1, seg2):
    pt1,pt2 = seg1
    pt3, pt4 = seg2
    if pt1[1] > pt2[1]:
        upper1 = pt1
    else:
        upper1 = pt2

    if pt3[1] > pt4[1]:
        upper2 = pt3
    else:
        upper2 = pt4

    if upper1[0] < upper2[0]:
        return upper1
    return upper2



class Shape():
    def __init__(self, outline, pic):
        self.outline = outline
        self.center = self.init_center()
        self.pic = pic
        self.corners = self.init_corners()

    def get_corners(self):
        return self.corners

    def init_center(self):
        x = 0
        y = 0
        for i in self.outline:
            x += i[0]
            y += i[1]
        return (int(x/len(self.outline)),  int(y/len(self.outline)))

    def get_center(self):
        return self.center
    def init_corners(self):

        x, y, w, h = boundingRect(self.outline)
        cropped = self.pic[x - 5:x+w + 5, y - 5:y+h + 5]
        hsv = toHSV.convertToHSV(cropped)
        channel2 = np.zeros((len(hsv), len(hsv[0])))
        for x in range(len(hsv)):
            for y in range(len(hsv[0])):
                channel2[x][y] = hsv[x][y][2]
        binaryImage = bi.createBinaryImage(channel2, 0, 1)

        # binaryImage = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
        c = gftt.goodFeaturesToTrack(binaryImage, 25,.8)
        corners = []
        if len(c) != 4 or not nearby(c, self.get_center(), 200):
            return self.get_bad_corners()
        for i in c:
            x1, y1 = i
            x1 += x - 5
            y1 += y - 5
            corners += [[int(x1),int(y1)]]
        return corners

    def init_orientation(self, corners=None):   #assume segments are ordered correctly i.e. corners[0] is adjacent to corners[1] and corners[3]
        if corners is None:
            corners = self.corners
        try:
            return math.atan((corners[0][1] - corners[1][1])/(corners[0][0] - corners[1][0]))
        except (ZeroDivisionError):
            return 90
    def draw(self, color=(0,255,0), thickness=2, pic=None):
        if pic is None:
            pic = self.pic
        cv2.line(pic, (self.corners[0][0], self.corners[0][1]), (self.corners[1][0], self.corners[1][1]), color, thickness)
        cv2.line(pic, (self.corners[2][0], self.corners[2][1]), (self.corners[1][0], self.corners[1][1]), color, thickness)
        cv2.line(pic, (self.corners[2][0], self.corners[2][1]), (self.corners[3][0], self.corners[3][1]), color, thickness)
        cv2.line(pic, (self.corners[0][0], self.corners[0][1]), (self.corners[3][0], self.corners[3][1]), color, thickness)

    def order_corners(self, corners):
        pt1 = corners[0]
        pt2 = corners[1]
        pt3 = corners[2]
        pt4 = corners[3]
        try:
            m1 = math.atan((pt1[1] - pt2[1]) / (pt1[0] - pt2[0]))
        except:
            m1 = math.pi / 2

        try:
            m2 = math.atan((pt3[1] - pt4[1]) / (pt3[0] - pt4[0]))
        except:
            m2 = math.pi / 2
        lst = []
        if m1 - .17 < m2 and m1 + .17 > m2:  # lines are parallel- opposite sides
            if significantly_different(pt1[1], pt2[1]):
                if pt1[1] > pt2[1] and pt3[1] > pt4[1]:
                    lst = [pt1, pt2, pt4, pt3]
                elif pt1[1] > pt2[1] and pt3[1] < pt4[1]:
                    lst = [pt1, pt2, pt3, pt4]
                elif pt1[1] < pt2[1] and pt3[1] > pt4[1]:
                    lst = [pt1, pt2, pt3, pt4]
                else:
                    lst = [pt1, pt2, pt4, pt3]
            else:
                if pt1[0] > pt2[0] and pt3[0] > pt4[0]:
                    lst = [pt1, pt2, pt4, pt3]
                elif pt1[0] > pt2[0] and pt3[0] < pt4[0]:
                    lst = [pt1, pt2, pt3, pt4]
                elif pt1[0] < pt2[0] and pt3[0] > pt4[0]:
                    lst = [pt1, pt2, pt3, pt4]
                else:
                    lst = [pt1, pt2, pt4, pt3]
        else:  # lines are not parallel
            lst = [pt1, pt3, pt2, pt4]
        self.corners = lst
        self.orientation = math.degrees(self.init_orientation())

    def get_orientation(self):
        return self.orientation

    def get_bad_corners(self):
        corners = []
        p = sorted(self.perimeter, key=self.dist, reverse=True)
        while len(corners) < 4 and p != []:
            if not nearby(corners, p[0], 30) and nearby([self.get_center()],p[0], 200):
                corners.append(p[0])
            p = p[1:]
        return corners



    def dist(self, pt):
        return ((self.center[0] - pt[0]) ** 2 + (self.center[1] - pt[1]) ** 2)** .5

def nearby(pts, pt, distance=25):
    for i in pts:
        if ((pt[0] - i[0]) ** 2 + (pt[1] - i[1]) ** 2)** .5 < distance:
            return True
    return False

def significantly_different(x1, x2):
    return x1 - 10 > x2 or x1 + 10 < x2

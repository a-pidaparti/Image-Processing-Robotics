import cv2
import numpy as np
import json
import shapes
import customBlobDetection as cbd
import convertToHSV as toHSV
import createBinaryImage as bi

distance_ratio_x = 0
distance_ratio_y = 0


def remove_array(L,arr):
    ind = 0
    size = len(L)
    while ind != size and not np.array_equal(L[ind],arr):
        ind += 1
    if ind != size:
        L.pop(ind)
    else:
        raise ValueError('array not found in list.')


# generates a list of corners. List sorted in order of strongest corners by opencv
# corner numbers appear consistent even thorugh rotation of board
def get_corners(pic):
    pts = [[0, 0], [0, 0], [0, 0]]
    lst = []
    objects = cbd.blobDetect(pic, 0.90, 1, 2)
    for i in range(3):
        c = max(objects)
        pts[i][0], pts[i][1] = c.get_center()
        lst += [(pts[i][0], pts[i][1])]
        remove_array(objects, c)
    return lst
# returns a list of 3-tupes of form (x, y, radius) of objects.
def get_objects(pic):
    objects = cbd.blobDetect(pic, .6, .8,2)
    return objects

def set_distance_ratio(corners): # sets global variable that is the ratio of a single pixel to real world distance
    global distance_ratio_x
    global distance_ratio_y
    x, y = corners[0]
    x_x, x_y = corners[2]
    y_x, y_y = corners[1]
    distance_ratio_x = abs(295.275/(x-x_x))
    distance_ratio_y = abs(403.225/(y-y_y))


def distance_between(obj, corners):
    #TODO add support for multiple orientaitons
    #TODO don't hard code support for only objects and corners.
    ox = obj.get_center()[0]
    oy = obj.get_center()[1]
    cx, cy = corners
    return abs(ox-cx) * distance_ratio_x, abs(oy - cy) * distance_ratio_y

def generate_json(pic):
    corners = get_corners(pic)
    objects = get_objects(pic)
    # hard coded in. Corner 7->4 gets us black space in x axis and 7->8 gets black space in y axis. (img.jpeg reference)
    set_distance_ratio(corners)
    xCoordList, yCoordList, zCoordList, rzCoordList, outputCoordList = [], [], [], [], []
    for object in objects:
        object.draw(color=(0,0,255))
        #abstracted away for possible future upgrade of allowing more than one orientation
        d1,d2 = distance_between(object, corners[0])
        xCoordList.append(d1)
        yCoordList.append(d2)
        zCoordList.append(0)
        rzCoordList.append(object.get_orientation())
    with open('data.json', 'w') as outfile:
        outputCoordList = [{"x": d1, "y": d2, "z": z, "rz": rz} for d1, d2, z, rz in zip(xCoordList, yCoordList, zCoordList, rzCoordList)]
        json.dump(outputCoordList, outfile)

if __name__ == "__main__":
    img = cv2.imread('img/rectanglesmin.jpg')
    generate_json(img)
    cv2.imshow("img",img)
    cv2.waitKey(0)



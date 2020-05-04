import numpy as np
import cv2
import convertToHSV as toHSV
import createBinaryImage as bi

np.warnings.filterwarnings('ignore')
def conv(img, kernel):

    img_height = img.shape[0]
    img_width = img.shape[1]
    pad_height = kernel.shape[0] // 2
    pad_width = kernel.shape[1] // 2
    # Allocate result image.
    pad = ((pad_height, pad_height), (pad_height, pad_width))
    g = np.empty(img.shape, dtype=np.float64)
    img = np.pad(img, pad, mode='constant', constant_values=0)
    # Do convolution
    for i in np.arange(pad_height, img_height+pad_height):
        for j in np.arange(pad_width, img_width+pad_width):
            roi = img[i - pad_height:i + pad_height +
                      1, j - pad_width:j + pad_width + 1]
            g[i - pad_height, j - pad_width] = (roi*kernel).sum()

    if (g.dtype == np.float64):
        kernel = kernel / 255.0
        kernel = (kernel*255).astype(np.uint8)
    else:
        g = g + abs(np.amin(g))
        g = g / np.amax(g)
        g = (g*255.0)

    return g

def goodFeaturesToTrack(pic, num=4, threshold=.6):
    sob_x = np.array(([-1,0,1], [-2, 0, 2], [-1 ,0 ,1]), dtype=np.uint8)
    sob_y = np.array(([1, 2, 1],[0,0,0],[-1,-2,-1]), dtype=np.uint8)
    gauss = np.array(([1/16, 2/16, 1/16], [2/16, 4/16, 2/16], [1/16, 2/16, 1/16]), dtype="float64")
    dx = conv(pic, sob_x)
    dy = conv(pic, sob_y)
    dx2 = np.square(dx)
    dy2 = np.square(dy)
    dxdy = dx * dy
    gauss_dx2 = conv(dx2, gauss)
    gauss_dy2 = conv(dy2, gauss)
    gauss_dxdy = conv(dxdy, gauss)


    goodFeaturesToTrack = gauss_dx2 * gauss_dy2 - np.square(gauss_dxdy) - 0.04 * np.square(gauss_dx2 + gauss_dy2)
    cv2.normalize(goodFeaturesToTrack, goodFeaturesToTrack, 0, 1, cv2.NORM_MINMAX)

    pts = np.where(goodFeaturesToTrack >= threshold)
    pts = list(zip(*pts[::-1]))

    def compare(pt):
        if pt[0] < 0 or pt[0] >= goodFeaturesToTrack.shape[0] or pt[1] < 0 or pt[1] >= goodFeaturesToTrack.shape[1]:
            return -1
        return goodFeaturesToTrack[pt[0], pt[1]]

    pts.sort(key=compare)
    realPts = []
    count = 0

    while pts != []:
        if not nearby(realPts, pts[0], 25):
            realPts += [[pts[0][0], pts[0][1]]]
            count += 1
        pts = pts[1:]
    return realPts

def nearby(pts, pt, distance=25):
    for i in pts:
        if ((pt[0] - i[0]) ** 2 + (pt[1] - i[1]) ** 2)** .5 < distance:
            return True
    return False

# def pts_manager(mat, pt):
#     if mat[pt[1], pt[0]] == 0:
#         return False
#     xmin = max(0, )
import cv2
import numpy as np
img = cv2.imread('ans/2--11-15-14-9.png')
origin = cv2.cvtColor(img[490:553, 225:305],cv2.COLOR_BGR2GRAY)
ret1, origin = cv2.threshold(origin, 0, 255, cv2.THRESH_BINARY)
runners = cv2.cvtColor(img[362:475, 39:500],cv2.COLOR_BGR2GRAY)
ret2, runners = cv2.threshold(runners, 85, 255, cv2.THRESH_BINARY)
sift = cv2.xfeatures2d.SIFT_create()
kp1, des1 = sift.detectAndCompute(origin, None)
FLANN_INDEX_KDTREE = 0
index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=4)
search_params = dict(checks=100)
flann = cv2.FlannBasedMatcher(index_params, search_params)
good_index = []
kp2, des2 = sift.detectAndCompute(runners, None)
matches = flann.knnMatch(des1, des2, k=2)
good = []
for m, n in matches:
    if m.distance < 0.7 * n.distance:
        good.append(m)
homography = []
print(len(good))
if len(good) >= 1:
    src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
    dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
    M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 10)
    maskmatches = mask.ravel().tolist()

    for index, pts in enumerate(good):
        if maskmatches[index] == 1:
            homography.append(pts)
draw_params = dict(matchColor=(0, 255, 0),  # draw matches in green color
                           singlePointColor=None,
                           matchesMask=None,  # draw only inliers
                           flags=2)

img3 = cv2.drawMatches(origin, kp1, runners, kp2, homography, None, **draw_params)
cv2.imshow('image', img3)
cv2.waitKey(0)
cv2.destroyAllWindows()
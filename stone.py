import elem
import cv2 as cv
import numpy as np
import time
#20 680  56*56

def get_stone_table(pic):
    #gray = cv.cvtColor(pic, cv.COLOR_RGB2GRAY)
    gray = pic
    x, y = 20, 680
    lis = []
    for j in range(0, 4):
        temp_list = []
        for i in range(0, 8):
            temp = gray[(y + j * 56):(y + j * 56 + 56), (x + i * 56):(x + i * 56 + 56)]
            #ret, temp2 = cv.threshold(temp, 0, 255, cv.THRESH_BINARY)
            temp_list.append(temp)
        lis.append(temp_list)
    return lis

def find_similar(pics,pic1):
    sift = cv.xfeatures2d.SIFT_create()
    kp2,des2 = sift.detectAndCompute(pic1,None)
    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=4)
    search_params = dict(checks=100)
    flann = cv.FlannBasedMatcher(index_params, search_params)
    good_index=[]
    for index,p in enumerate(pics):
        kp1,des1 = sift.detectAndCompute(p,None)
        matches = flann.knnMatch(des1, des2, k=2)
        good = []
        for m, n in matches:
            if m.distance < 0.7 * n.distance:
                good.append(m)
        if len(good) >= 7:
            good_index.append(index)
    return good_index
def find_x_y(lis,pic):
    x_y_list =[]
    for y,plist in enumerate(lis):
        x_index = find_similar(plist,pic)
        for x in x_index:
            x_y_list.append([x,y])
    return x_y_list
blank = cv.imread('blank.png')
blank = cv.cvtColor(blank, cv.COLOR_RGB2GRAY)
def check_blank(pic):
    pic = cv.cvtColor(pic,cv.COLOR_RGB2GRAY)
    ret, pic = cv.threshold(pic, 0, 255, cv.THRESH_BINARY)
    if np.array_equal(blank,pic):
        return 1
    else:
        return 0
def x_y_to_pixel(x,y):
    p_x = x*56+56/2+20
    p_y = y*56+56/2+680
    return p_x,p_y

if __name__ =="__main__":
    root = "C:\ChangZhi2\dnplayer2\\"
    con = elem.controller(root,1)
    while 1:
        try:
            con.screenshot("/sdcard/temp.png")
            con.pull("/sdcard/temp.png", "temp.png")
            pic = cv.imread('temp.png')
            time.sleep(2)
            lis = get_stone_table(pic)
            mod_list = []
            # stone_table = []
            # for l in lis:
            #     temp_table = []
            #     for p in l:
            #         if not check_blank(p):
            #             temp_table.append(1)
            #         else:
            #             temp_table.append(0)
            #     stone_table.append(temp_table)
            # move_table = []
            # for level,chest in enumerate(stone_table):
            #     for index,stone in enumerate(chest):
            #         if level == 0 and stone == 0:
            #             move_table.append([])

            for j, l in enumerate(lis):
                for i, p in enumerate(l):
                    if not check_blank(p):
                        try:
                            xy = find_x_y(lis, p)
                            if len(xy) == 2:
                                x0, y0 = x_y_to_pixel(i, j)
                                x1, y1 = x_y_to_pixel(xy[1][0], xy[1][1])
                                if [x0, y0] != [x1, y1] and [x1, y1] not in mod_list:
                                    con.swipe(x0, y0, x1, y1, 150)
                                    mod_list.append([x1, y1])
                            elif len(xy) > 2:
                                x0, y0 = x_y_to_pixel(i, j)
                                for x, y in xy:
                                    x1, y1 = x_y_to_pixel(x, y)
                                    if [x0, y0] != [x1, y1] and [x1, y1] not in mod_list:
                                        con.swipe(x1, y1, x0, y0, 150)
                                        mod_list.append([x1, y1])
                                        x0, y0 = x1, y1
                        except:
                           print("error")




        except:
            print("FUCK")
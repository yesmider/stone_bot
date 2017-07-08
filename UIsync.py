import cv2
import numpy as np
import elem
import logging
import os
#import tempfile as tf
#from pynput import keyboard
# todo keyboard listener
# todo autodetect and donate coin to clan

class Stone_UI:
    """
    this class is for UI detection
    """
    def __init__(self,dnpath = 'C:\ChangZhi2\dnplayer2\\', emulator_name="1", ad=False):
        self.controller = elem.controller(dnpath,emulator_name)
        self.temp = 'temp\\temp.png'
        self.ad = ad
        self.img_refresh()
        self.quiz_banner = cv2.imread('pics/quiz_banner.png')
        self.KAZE = cv2.KAZE_create()
        self.BF = cv2.BFMatcher()
        self.train_path = 'color_train'
        self.pic_dict = {
        }
        self.train_init()
    def train_init(self):
        train = [f for f in os.listdir(self.train_path) if os.path.isdir(os.path.join(self.train_path, f)) and f != 'compare']
        for dir in train:
            l = []
            full_path = os.path.join(self.train_path, dir)
            files = [os.path.join(full_path, f) for f in os.listdir(full_path) if
                     os.path.isfile(os.path.join(full_path, f))]
            for file in files:
                logging.info('loading file - {}'.format(file))
                img = cv2.imread(file)
                # img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                # ret1, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY)
                kp, des = self.KAZE.detectAndCompute(img, None)
                l.append((img, kp, des))
            self.pic_dict[dir] = l
        logging.info('train_data_init done.')
    def screenshot(self):
        con = self.controller
        con.screenshot(filepath='/sdcard/Misc/temp.png')
        con.pull_screenshot(target_file='/sdcard/Misc/temp.png',file_name=self.temp)

    def img_refresh(self):
        self.screenshot()
        self.img =cv2.imread(self.temp) # img in RGB
        self.pic = cv2.cvtColor(self.img,cv2.COLOR_BGR2HSV)#in HSV

    def softmax(self, w):
            """Calculate the softmax of a list of numbers w.

                Parameters
                ----------
                w : list of numbers

                Return
                ------
                a list of the same length as w of non-negative numbers

                Examples
                --------
    """
            e = np.exp(np.array(w))
            dist = e / np.sum(e)
            return dist

    def check_game_active(self):
        game = self.controller.get_now_activity_windows()
        if game == "net.supercat.stone/net.supercat.stone.MainActivity":
            return True
        elif game is None:
            return None
        else:
            return False

    def check_quiz_pop(self):
        runners = self.img[362:475, 39:500]
        origin = self.img[490:590, 225:315]
        kp1, des1 = self.KAZE.detectAndCompute(origin, None)
        kp2, des2 = self.KAZE.detectAndCompute(runners, None)
        # check runners bound box postion
        range_x = []
        for value in kp2:
            x = value.pt[0]
            range_x.append(x)
        std_range = np.std(range_x)
        mean_range = np.mean(range_x)

        max_x, min_x = mean_range + std_range * 1.5, mean_range - std_range * 1.5
        x0, x1, x2, x3, x4 = min_x, (max_x - min_x) / 4 + min_x, (max_x - min_x) / 2 + min_x, (
        max_x - min_x) * 3 / 4 + min_x, max_x
        # check origin ans
        ans_dict = {
            '0': 0,
            '1': 0,
            '2': 0,
            '3': 0,
            '4': 0,
            '5': 0,
            '6': 0
        }
        for key,value in self.pic_dict.items():
            for img,kp,des in value:
                matches = self.BF.knnMatch(des1,des,k=2)
                good = []
                for m,n in matches:
                    if m.distance < 0.7 * n.distance:
                        good.append([m])
                ans_dict[key] += len(good)
        v = list(ans_dict.values())
        k = list(ans_dict.keys())
        ans = k[v.index(max(v))]
        # print(ans_dict)
        # use ans result to compare runners
        vote = {
            1: 0,
            2: 0,
            3: 0,
            4: 0
        }
        for img,kp,des in self.pic_dict[ans]:
            matches = self.BF.knnMatch(des,des2,k=2)
            good = []
            for m, n in matches:
                if m.distance < 0.8 * n.distance:
                    good.append([m])
            # print(len(good))
            if len(good)>1:
                for [value] in good:
                    x = kp2[value.trainIdx].pt[0]
                    if x < x0:
                        vote[1] += 1
                    elif x0 < x < x1:
                        vote[1] += 2
                        vote[2] += 1
                    elif x1 < x < x2:
                        vote[1] += 1
                        vote[2] += 2
                        vote[3] += 1
                    elif x2 < x < x3:
                        vote[2] += 1
                        vote[3] += 2
                        vote[4] += 1
                    elif x3 < x < x4:
                        vote[3] += 1
                        vote[4] += 2
                    elif x4 < x:
                        vote[4] += 1

        draw_params = dict(matchColor=(0, 255, 0),
                           singlePointColor=(255, 0, 0),
                           flags=2)
        img3 = cv2.drawMatchesKnn(img, kp, runners, kp2, good, None, **draw_params)
        # print(vote)
        return img3, vote

    def check_ruby_box(self):
        """
        checking ruby box on the right side , using the sift to  compare the bottom icon of ruby bot
        :return:  the axis of ruby box touch point
        """
        ruby_box = self.img[910:940,138:169]
        ruby_area = self.img[400:650,0:80]
        sift = cv2.xfeatures2d.SIFT_create()
        kp1, des1 = sift.detectAndCompute(ruby_box, None)
        kp2, des2 = sift.detectAndCompute(ruby_area, None)
        FLANN_INDEX_KDTREE = 0
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=4)
        search_params = dict(checks=100)
        flann = cv2.FlannBasedMatcher(index_params, search_params)
        good_index = []
        matches = flann.knnMatch(des1, des2, k=2)
        #print(len(matches))
        good = []
        for m, n in matches:
            if m.distance < 0.7 * n.distance:
                good.append(m)
        if len(good) >= 2:
            x = 0
            y = 0
            for value in good:
                x += kp2[value.trainIdx].pt[0]
                y += kp2[value.trainIdx].pt[1]
            x = x/len(good)
            y = y / len(good)
            return x,y+400
        else:
            return None

    def check_fast_mining(self):
        fast_mining = cv2.imread('pics/fast_mining.png')
        ruby_area = self.img[400:650,0:80]
        sift = cv2.xfeatures2d.SIFT_create()
        kp1, des1 = sift.detectAndCompute(fast_mining, None)
        kp2, des2 = sift.detectAndCompute(ruby_area, None)
        FLANN_INDEX_KDTREE = 0
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=4)
        search_params = dict(checks=100)
        flann = cv2.FlannBasedMatcher(index_params, search_params)
        good_index = []
        matches = flann.knnMatch(des1, des2, k=2)
        good = []
        for m, n in matches:
            if m.distance < 0.7 * n.distance:
                good.append([m])
        # print(good)
        if len(good) >= 1:
            x = 0
            y = 0
            for [value] in good:
                x += kp2[value.trainIdx].pt[0]
                y += kp2[value.trainIdx].pt[1]
            x = x/len(good)
            y = y/len(good)
            return x,y+400
        else:
            return None
    def check_mining_or_mob(self):
        """
        check player is in mining fields or mod fields
        :return: string : mob or mining
        """
        mining = cv2.imread('pics/mining.png')
        if mining is None:
            while mining is not None:
                self.img_refresh()
                mining = cv2.imread('pics/mining.png')
        if self.ad is True:
            check_point = self.img[106:108,344:346]
        else:
            check_point = self.img[196:198, 344:346]
        if np.equal(check_point,mining).all():
            return 'mob'
        else:
            return 'mining'
    def check_clan_windows(self):
        """
        check the clan title in the clan tabs
        :return: truth
        """
        clan = cv2.imread('pics/clan.png')
        if np.array_equal(self.img[122:137,254:286],clan):
            return True
        else:
            return False
    def check_stone_box_statue(self):
        #  X = 495 1 690 720 2 745 770 3 850 880 4 900 935
        """
        check the stone box UI is Turn on or not.
        :return: truth
        """
        x = 495
        y_axis1 = [690,745,850,900]
        y_axis2 = [720,770,880,935]
        button_stat = []
        for i in range(len(y_axis1)):
            if self.pic[y_axis1[i],x].item(0) == 13 and self.pic[y_axis2[i],x].item(0) == 10:
                button_stat.append(1)
            else:
                button_stat.append(0)
        COUNT = 0
        for b in button_stat:
            if b == 1:
                COUNT += 1
        if COUNT == 4:
            return True
        elif COUNT == 1:
            return False
        else:
            return None
    def check_pop_box_statue(self):
        """
        detect the pop box
        :return: truth
        """
        if self.check_stone_box_statue() is None:
            return True
        else:
            return False

    def check_auto_attack_statue(self):
        """
        check the auto attack statue , # stone box must be Turn off
        :return: truth , None if the stone box is turned on.
        """

        if self.check_stone_box_statue() is False:
            if self.pic[850,430].item(0) == 18 and self.pic[850,490].item(0) == 18:
                return True
            else:
                return False
        else:
            return None

    def check_reward_statue(self):
        if self.ad is False:
            if self.pic[190, 483].item(0) == 0 and self.pic[180, 492].item(0) == 0:
                return True
            else:
                return False
        else:
            if self.pic[100, 483].item(0) == 0 and self.pic[90, 492].item(0) == 0:
                return True
            else:
                return False
    def __stone_table(self,pic):
        """
        cut the screenshots into the pic of stone, one by one
        :param pic: must be RGB
        :return:list of stone
        """
        x,y = 20,680
        stone_list = []
        for j in range(0,4):
            temp_list = []
            for i in range(0,8):
                temp = pic[(y + j * 56):(y + j * 56 + 56), (x + i * 56):(x + i * 56 + 56)]
                temp_list.append(temp)
            stone_list.append(temp_list)
        return stone_list

    def __stone_table_truth(self,stone_table):
        """

        :param stone_table: the table generate from __stone_table
        :return:truth_table of stone
        """
        blank = cv2.cvtColor(cv2.imread('pics/blank.png'), cv2.COLOR_BGR2GRAY)
        truth_table = []
        for x in stone_table:
            temp_list = []
            for pic in x:
                pic = cv2.cvtColor(pic, cv2.COLOR_BGR2GRAY)
                ret, pic = cv2.threshold(pic, 0, 255, cv2.THRESH_BINARY)
                if np.array_equal(blank, pic):
                    temp_list.append(0)
                else:
                    temp_list.append(1)
            truth_table.append(temp_list)
        truth_table[0] = [0,0,0,0,0,0,0,0]
        return truth_table

    def x_y_to_pixel(self,x,y):
        """
        x and y is the axis of stone in stone table
        :param x: the axis x of stone in stone table
        :param y: the axis y of stone in stone table
        :return: x,y in the screenshots
        """
        p_x = x * 56 + 56 / 2 + 20
        p_y = y * 56 + 56 / 2 + 680
        return p_x, p_y

    def compare_stone(self,stone,stone_table):
        """

        :param stone:img from __stone_table
        :param stone_table: __stone_table result
        :return: same stone pos list
        """
        sift = cv2.xfeatures2d.SIFT_create()
        kp1,des1 = sift.detectAndCompute(stone,None)
        FLANN_INDEX_KDTREE = 0
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=4)
        search_params = dict(checks=100)
        flann = cv2.FlannBasedMatcher(index_params, search_params)
        good_index = []
        for y,list in enumerate(stone_table):
            for x,pic in enumerate(list):
                kp2, des2 = sift.detectAndCompute(pic, None)
                matches = flann.knnMatch(des1, des2, k=2)
                good = []
                for m, n in matches:
                    if m.distance < 0.4 * n.distance:
                        good.append(m)
                homography = []
                if len(good) >=5:
                    src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
                    dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
                    M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
                    maskmatches = mask.ravel().tolist()
                    for index,pts in enumerate(good):
                        if maskmatches[index] == 1:
                            homography.append(pts)
                if len(homography) >=5:
                    good_index.append(self.x_y_to_pixel(x,y))

                    # draw_params = dict(matchColor=(0, 255, 0),  # draw matches in green color
                    #                    singlePointColor=None,
                    #                    matchesMask=None,  # draw only inliers
                    #                    flags=2)
                    #
                    # img3 = cv2.drawMatches(stone, kp1, pic, kp2, homography, None, **draw_params)
                    # cv2.imshow('image', img3)
                    # cv2.waitKey(0)
                    # cv2.destroyAllWindows()
        return good_index

    def check_stone_pairs(self):
        """

        :return:
        """
        stone_table = self.__stone_table(self.img)
        truth_table = self.__stone_table_truth(stone_table)
        pairs = []
        # get pairs
        if self.check_stone_box_statue() is True:
            for y in range(len(truth_table)):
                for x in range(len(truth_table[y])):
                    if truth_table[y][x] == 1:
                        main_stone = stone_table[y][x]
                        pair = self.compare_stone(main_stone,stone_table)
                        if len(pair)>1 and pair not in pairs:
                            pairs.append(pair)
        return pairs

    def vote_quiz(self):
        """

        :return:
        """
        main_vote = {1: 0,
                     2: 0,
                     3: 0,
                     4: 0}
        count = 0
        while count <= 50:
            quiz, vote = self.check_quiz_pop()
            # cv2.imwrite('quiz/{}.png'.format(time.time()), quiz)
            for key in vote.keys():
                main_vote[key] += vote[key]

            self.img_refresh()
            count += 1
        v = list(main_vote.values())
        k = list(main_vote.keys())
        logging.info('vote_result = {}'.format(v))
        ans = k[v.index(max(v))]
        value = "{}-{}-{}-{}".format(v[0],v[1],v[2],v[3])
        cv2.imwrite('ans/{}--{}.png'.format(ans,value), self.img)
        return v,ans

    def check_rain(self):
        if self.ad is False:
            check_poing = self.pic[147,337].item(0)
        else:
            check_poing = self.pic[56,337].item(0)

        if check_poing == 0:
            logging.info('the weather is raining.')
            return True
        else:
            return False



if __name__ =="__main__":
    pass




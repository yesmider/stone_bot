import cv2
import numpy as np
import elem
import logging
import os
import time
import screencap
from multiprocessing.pool import ThreadPool
import multiprocessing
#from pynput import keyboard
# todo keyboard listener
# todo autodetect and donate coin to clan

class Stone_UI:
    """
    this class is for UI detection
    """
    def __init__(self,dnpath = 'C:\ChangZhi2\dnplayer2\\', emulator_name="1", ad=False,adb_mode = False):

        self.controller = elem.controller(dnpath,emulator_name)
        self.temp = 'temp\\temp.png'
        self.ad = ad
        self.adb_mode = adb_mode
        if self.adb_mode:
            self.port = self.controller.get_port_by_name(emulator_name)
        self.img_refresh()
        self.quiz_banner = cv2.imread('pics/quiz_banner.png')

        self.train_path = 'color_train'
        self.pics_path = 'pics'
        self.quiz_pics = {
        }
        self.pics = {

        }
        self.train_init()
    def train_init(self):
        KAZE = cv2.KAZE_create()

        train = [f for f in os.listdir(self.train_path) if os.path.isdir(os.path.join(self.train_path, f)) and f != 'compare']
        pics = [f for f in os.listdir(self.pics_path) if os.path.isfile(os.path.join(self.pics_path,f))]
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
                kp, des = KAZE.detectAndCompute(img, None)
                l.append((img, kp, des))
            self.quiz_pics[dir] = l
        for pic_name in pics:
            logging.info('loading file - {}'.format(pic_name))
            full_path = os.path.join(self.pics_path,pic_name)
            img = cv2.imread(full_path)
            self.pics[pic_name] = img
        logging.info('train_data_init done.')
    def screenshot(self):
        if self.adb_mode is False:
            con = self.controller
            con.screenshot(filepath='/sdcard/Misc/temp.png')
            con.pull_screenshot(target_file='/sdcard/Misc/temp.png', file_name=self.temp)
            self.img = cv2.imread(self.temp)
        else:
            self.img = screencap.adb_screen_cap(self.port)


    def img_refresh(self):
        self.screenshot()
        while self.img is None:
            self.screenshot()
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

    def check_Alert_box(self):
        check_point1 = self.pic[564,240]
        check_point2 = self.pic[564,372]
        check_point3 = self.pic[564,245]
        if (check_point1.item(0) == 19 and check_point2.item(0) == 0) or check_point3.item(0) == 19:
            logging.info('Alert box.')
            return True
        else:
            logging.info('Nothing.')
            return False
    # break
    def check_mining_text(self):
        text = self.img[410:535,125:415]
        fast_mining = self.pics['fast_mining_text_cht.png']
        faster_mining = self.pics['faster_mining_text_cht.png']
        if np.array_equal(text,fast_mining):
            logging.info('fast mining.')
            return 0
        elif np.array_equal(text,faster_mining):
            logging.info('faster mining.')
            return 1
        else:
            logging.info('Nothing.')
            return 2

    def check_bonus_ruby(self):
        KAZE = cv2.KAZE_create()
        BF = cv2.BFMatcher()
        ruby_area = self.img[370:650, 0:80]
        bonus_ruby = self.pics['bonus_ruby.png']
        kp1,des1 = KAZE.detectAndCompute(bonus_ruby,None)
        kp2,des2 = KAZE.detectAndCompute(ruby_area,None)
        if kp2:
            matches = BF.knnMatch(des1, des2, k=2)
            good = []
            append = good.append
            for m, n in matches:
                if m.distance < n.distance * 0.7:
                    append([m])
            if len(good) >= 2:
                good_trainIdx = [value.trainIdx for [value] in good]
                x = sum([kp2[idx].pt[0] for idx in good_trainIdx])/len(good)
                y = sum([kp2[idx].pt[1] for idx in good_trainIdx])/len(good)
                return x, y + 370

    def check_game_active(self):
        game = self.controller.get_now_activity_windows()
        if game == "net.supercat.stone/net.supercat.stone.MainActivity":
            return True
        elif game is None:
            return None
        else:
            return False



    def check_ruby_box(self):
        """
        checking ruby box on the right side , using the sift to  compare the bottom icon of ruby bot
        :return:  the axis of ruby box touch point
        """
        ruby_box = self.pics['box.png']
        ruby_area = self.img[370:650,0:80]
        sift = cv2.xfeatures2d.SIFT_create()
        kp1, des1 = sift.detectAndCompute(ruby_box, None)
        kp2, des2 = sift.detectAndCompute(ruby_area, None)
        if kp2:
            FLANN_INDEX_KDTREE = 0
            index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=4)
            search_params = dict(checks=100)
            flann = cv2.FlannBasedMatcher(index_params, search_params)
            matches = flann.knnMatch(des1, des2, k=2)
            # print(len(matches))
            good = [[m] for m,n in matches if m.distance < 0.7 * n.distance]
            if len(good) >= 2:
                good_trainIdx = [value.trainIdx for [value] in good]
                x = sum([kp2[idx].pt[0] for idx in good_trainIdx])/len(good)
                y = sum([kp2[idx].pt[1] for idx in good_trainIdx])/len(good)
                return x, y + 370
            else:
                return None

    def check_fast_mining(self):
        fast_mining = self.pics['fast_mining.png']
        ruby_area = self.img[370:650,0:80]
        sift = cv2.xfeatures2d.SIFT_create()
        kp1, des1 = sift.detectAndCompute(fast_mining, None)
        kp2, des2 = sift.detectAndCompute(ruby_area, None)
        if kp2:
            FLANN_INDEX_KDTREE = 0
            index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=4)
            search_params = dict(checks=100)
            flann = cv2.FlannBasedMatcher(index_params, search_params)
            matches = flann.knnMatch(des1, des2, k=2)
            good = [[m] for m,n in matches if m.distance < 0.7 * n.distance]
            # print(good)
            if len(good) >= 1:
                good_trainIdx = [value.trainIdx for [value] in good]
                x = sum([kp2[idx].pt[0] for idx in good_trainIdx])/len(good)
                y = sum([kp2[idx].pt[1] for idx in good_trainIdx])/len(good)
                return x, y + 370
            else:
                return None
    def check_mining_or_mob(self):
        """
        check player is in mining fields or mod fields
        :return: string : mob or mining
        """
        mining = self.pics['mining.png']
        check_point = self.img[106:108,344:346] if self.ad is True else self.img[196:198, 344:346]
        return 'mob' if np.array_equal(check_point,mining) else 'mining'


    def check_stone_box_statue(self):
        #  X = 495 1 690 720 2 745 770 3 850 880 4 900 935
        """
        check the stone box UI is Turn on or not.
        :return: truth
        """
        x = 495
        y_axis1 = [690,745,850,900]
        y_axis2 = [720,775,880,935]
        button_stat = [1 if self.pic[y_axis1[i],x].item(0) == 13 and self.pic[y_axis2[i],x].item(0) == 10\
                           else 0 for i in range(4)]
        COUNT = button_stat.count(1)
        return True if COUNT == 4 else False if COUNT == 1 else None

    def check_pop_box_statue(self):
        """
        detect the pop box
        :return: truth
        """
        return True if self.check_stone_box_statue() is None else False

    def check_auto_attack_statue(self):
        """
        check the auto attack statue , # stone box must be Turn off
        :return: truth , None if the stone box is turned on.
        """

        if self.check_stone_box_statue() is False:
            return True if self.pic[843,422].item(0) == self.pic[843,500].item(0) == 18 else False
        else:
            return None

    def check_reward_statue(self):
        if self.ad is False:
            return True if self.pic[190, 483].item(0) == self.pic[180, 492].item(0) == 0 else False
        else:
            return True if self.pic[100, 483].item(0) == self.pic[90, 492].item(0) == 0 else False

    def check_quiz_pop(self):
        KAZE = cv2.KAZE_create()
        BF = cv2.BFMatcher()
        runners = self.img[362:475, 39:500]
        origin = self.img[490:590, 225:315]
        kp1, des1 = KAZE.detectAndCompute(origin, None)
        kp2, des2 = KAZE.detectAndCompute(runners, None)
        # check runners bound box postion

        range_x = [value.pt[0] for value in kp2]

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
        for key,value in self.quiz_pics.items():
            for img,kp,des in value:
                matches = BF.knnMatch(des1,des,k=2)
                good = [[m] for m,n in matches if m.distance < 0.7 * n.distance]
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
        for img,kp,des in self.quiz_pics[ans]:
            matches = BF.knnMatch(des,des2,k=2)
            good = [[m] for m,n in matches if m.distance < 0.7 * n.distance]
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

        img3 = 0
        return img3, vote

    def vote_quiz(self):
        """

        :return:
        """
        with ThreadPool() as pool:
            main_vote = {1: 0,
                         2: 0,
                         3: 0,
                         4: 0}
            count = 0
            result = []
            while count <= 50:
                res = pool.apply_async(self.check_quiz_pop, ())
                # quiz, vote = self.check_quiz_pop()
                # cv2.imwrite('quiz/{}.png'.format(time.time()), quiz)
                # for key in vote.keys():
                #     main_vote[key] += vote[key]
                result.append(res)
                self.img_refresh()
                count += 1
            pool.close()
            pool.join()
            for value in result:
                quiz, vote = value.get()
                # print(value.get())
                for key in vote.keys():
                    main_vote[key] += vote[key]
            v = list(main_vote.values())
            k = list(main_vote.keys())
            logging.info('vote_result = {}'.format(v))
            ans = k[v.index(max(v))]

            # value = "{}-{}-{}-{}".format(v[0],v[1],v[2],v[3])
            # cv2.imwrite('ans/{}--{}.png'.format(ans,value), self.img)
            return v, ans

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

    @staticmethod
    def x_y_to_pixel(x, y):
        """
        x and y is the axis of stone in stone table
        :param x: the axis x of stone in stone table
        :param y: the axis y of stone in stone table
        :return: x,y in the screenshots
        """
        p_x = x * 56 + 56 / 2 + 20
        p_y = y * 56 + 56 / 2 + 680
        return p_x, p_y

    @staticmethod
    def __pic_masks(table_hsv):
        """
        generate mask for matching
        :return:
        """

        up = np.array([17, 0, 0])
        down = np.array([18, 127, 220])
        masks = [[cv2.bitwise_not(cv2.inRange(pic, up, down)) for pic in y]
                 for y in table_hsv]
        return masks
    @staticmethod
    def __stone_table(pic):
        """
        cut the screenshots into the pic of stone, one by one
        :param pic: must be RGB
        :return:list of stone
        """
        x, y = 20, 680
        stone_list = [[pic[(y + j * 56):(y + j * 56 + 56), (x + i * 56):(x + i * 56 + 56)] for i in range(0, 8)] for j
                      in range(0, 4)]
        return stone_list

    def __stone_table_truth(self,stone_table):
        """

        :param stone_table: the table generate from __stone_table
        :return:truth_table of stone
        """
        blank = cv2.cvtColor(self.pics['blank.png'], cv2.COLOR_BGR2GRAY)
        truth_table = []
        truth_append = truth_table.append
        for x in stone_table:
            temp_list = []
            temp_append = temp_list.append
            for pic in x:
                pic = cv2.cvtColor(pic, cv2.COLOR_BGR2GRAY)
                ret, thr_pic = cv2.threshold(pic, 0, 255, cv2.THRESH_BINARY)
                # print(pic[7,28],pic[44,28])
                if np.array_equal(blank, thr_pic):
                    temp_append(0)
                else:
                    temp_append(1)
            truth_append(temp_list)
        truth_table[0] = [0, 0, 0, 0, 0, 0, 0, 0]
        return truth_table
    @staticmethod
    def match(img1, msk1, img2, msk2):
        def color_compare(img1, mask1, img2, mask2):
            for i in range(3):
                hist1 = cv2.calcHist([img1], [i], mask1, [256], [0, 256])
                hist2 = cv2.calcHist([img2], [i], mask2, [256], [0, 256])
                res = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
                if res < 0.9:
                    return False
            return True

        KAZE = cv2.KAZE_create()
        BF = cv2.BFMatcher()
        kp, des = KAZE.detectAndCompute(img1,msk1)
        kp2, des2 = KAZE.detectAndCompute(img2, msk2)
        if len(kp2) > 2 and len(kp) > 2:
            matches = BF.knnMatch(des, des2, k=2)
            if len(matches) > 1:
                good = [m for m, n in matches if m.distance < 0.4 * n.distance]
                if len(good) > 0:
                    src_pts = np.float32([kp[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
                    dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
                    M, h_mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 1.0)
                    maskmatches = h_mask.ravel().tolist()
                    homography = [pts for index, pts in enumerate(good) if maskmatches[index] == 1]
                    if len(homography) > 0.7 * len(good) and color_compare(img1, msk1, img2, msk2):
                        return True
        return False
    def check_stone_pairs(self):
        """

        :return:
        """
        def calc_kp_des_hist_by_table(table,masks,checked):
            KAZE = cv2.KAZE_create()

            def calc_kp_des_hist(img,mask):
                kp,des = KAZE.detectAndCompute(img,mask)
                hist = [cv2.calcHist([img], [0], mask, [256], [0, 256]),cv2.calcHist([img], [1], mask, [256], [0, 256]),cv2.calcHist([img], [2], mask, [256], [0, 256])]
                return kp,des,hist

            with ThreadPool() as pool:
                results = []
                for y, data in enumerate(table):
                    temp = []
                    for x, pic in enumerate(data):
                        if (x, y) not in checked:
                            mask = masks[y][x]
                            res = pool.apply_async(calc_kp_des_hist, (pic, mask))
                            temp.append(res)
                        else:
                            res = None
                            temp.append(res)
                    results.append(temp)
                pool.close()
                pool.join()
                final = []
                for y in results:
                    temp = []
                    for kp_res in y:
                        if kp_res is not None:
                            kp, des, hist = kp_res.get()
                            if len(kp) > 0:
                                temp.append((kp, des, hist))
                            else:
                                temp.append(None)
                        else:
                            temp.append(None)
                    final.append(temp)
                return final

        def match(d1,d2):
            BF = cv2.BFMatcher()
            kp1, des1, hist_3channal1 = d1
            kp2, des2, hist_3channal2 = d2
            def color_compare(hist1,hist2):
                for i in range(3):
                    res = cv2.compareHist(hist1[i], hist2[i], cv2.HISTCMP_CORREL)
                    if res < 0.8:
                        return False
                return True

            if len(kp2) > 2 and len(kp1) > 2:
                matches = BF.knnMatch(des1, des2, k=2)
                if len(matches) > 1:
                    good = [m for m, n in matches if m.distance < 0.4 * n.distance]
                    if len(good) > 0:
                        src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
                        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
                        M, h_mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 1.0)
                        maskmatches = h_mask.ravel().tolist()
                        homography = [pts for index, pts in enumerate(good) if maskmatches[index] == 1]
                        if len(homography) > 0.7 * len(good) and color_compare(hist_3channal1,hist_3channal2):
                            return True
            return False


        stone_box_statue = self.check_stone_box_statue()
        # get pairs
        if stone_box_statue is True:
            t = time.time()
            count = 0
            bgr_stone_table = self.__stone_table(self.img)
            hsv_stone_table = self.__stone_table(self.pic)
            truth_table = self.__stone_table_truth(bgr_stone_table)
            masks = self.__pic_masks(hsv_stone_table)
            checked = [(x, y) for y, data in enumerate(truth_table) for x, res in enumerate(data) if res != 1]
            kp_des_hist = calc_kp_des_hist_by_table(bgr_stone_table, masks, checked)

            pairs = []
            for y,lis in enumerate(kp_des_hist):
                for x,data in enumerate(lis):

                    pair = []
                    if data and (x,y) not in checked:
                        for y1,lis1 in enumerate(kp_des_hist):
                            for x1,data1 in enumerate(lis1):
                                if data1:
                                    if match(data,data1):
                                        pair.append((x1,y1))
                                        # if (x1,y1) not in checked:
                                        #     checked.append((x1,y1))
                    if len(pair)>1:
                        temp = []
                        for x2,y2 in pair:
                            xy = self.x_y_to_pixel(x2,y2)
                            temp.append(xy)
                        pairs.append(temp)
                        count += 1
                    if (x,y) not in checked:
                        checked.append((x,y))

            t1 = time.time()
            logging.info('Spend {} sec for compute stone {} pair'.format(t1-t,count))
            return pairs
if __name__ =="__main__":
    ui = Stone_UI(emulator_name='2')
    print(ui.check_stone_pairs())

    # print(ui.controller.get_now_activity_windows())
    #net.supercat.stone/com.unity3d.ads.adunit.AdUnitActivity
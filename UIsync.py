import cv2
import numpy as np
import elem
import time
import random
#import tempfile as tf
#from pynput import keyboard
# todo keyboard listener
# todo autodetect and donate coin to clan
class Stone_UI:
    """
    this class is for UI detection
    """
    def __init__(self,dnpath = 'C:\ChangZhi2\dnplayer2\\',emulator_name = "1"):
        self.controller = elem.controller(dnpath,emulator_name)
        self.temp = 'temp\\temp.png'
        self.img_refresh()
        self.screenshot()
        self.img =cv2.imread(self.temp) # img in RGB
        self.pic = cv2.cvtColor(self.img,cv2.COLOR_BGR2HSV) #in HSV
        self.gray = cv2.cvtColor(self.img,cv2.COLOR_RGB2GRAY)
        self.quiz_banner = cv2.imread('pics/quiz_banner.png')
    def screenshot(self):
        con = self.controller
        con.screenshot(filepath='/sdcard/Misc/temp.png')
        con.pull_screenshot(target_file='/sdcard/Misc/temp.png',file_name=self.temp)

    def img_refresh(self):
        self.screenshot()
        self.img =cv2.imread(self.temp) # img in RGB
        self.pic = cv2.cvtColor(self.img,cv2.COLOR_BGR2HSV)#in HSV
        self.gray = cv2.cvtColor(self.img, cv2.COLOR_RGB2GRAY)
    def check_game_active(self):
        if self.controller.get_now_activity_windows() == "net.supercat.stone/net.supercat.stone.MainActivity":
            return True
        else:
            return False

    def chekc_quiz_pop(self):
        origin = cv2.cvtColor(self.img[490:553, 225:305],cv2.COLOR_RGB2GRAY)
        runners = cv2.cvtColor(self.img[362:475, 39:500],cv2.COLOR_RGB2GRAY)
        ret1, origin = cv2.threshold(origin, 0, 255, cv2.THRESH_BINARY)
        ret2, runners = cv2.threshold(runners, 70, 255, cv2.THRESH_BINARY)
        SURF = cv2.xfeatures2d.SURF_create()
        kp1, des1 = SURF.detectAndCompute(origin, None)
        kp2, des2 = SURF.detectAndCompute(runners, None)
        FLANN_INDEX_KDTREE = 0
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=4)
        search_params = dict(checks=100)
        flann = cv2.FlannBasedMatcher(index_params, search_params)
        range_x = []
        matches = flann.knnMatch(des1, des2, k=2)
        for value in kp2:
            x = value.pt[0]
            range_x.append(x)
        std_range = np.std(range_x)
        mean_range = np.mean(range_x)

        max_x, min_x = mean_range + std_range * 1.5, mean_range - std_range * 1.5
        x0, x1, x2, x3, x4 = min_x, (max_x - min_x) / 4 + min_x, (max_x - min_x) / 2 + min_x, (
        max_x - min_x) * 3 / 4 + min_x, max_x

        good = []
        for m, n in matches:
            if m.distance < 0.7 * n.distance:
                good.append([m])
        draw_params = dict(matchColor=(0, 255, 0),
                           singlePointColor=(255, 0, 0),
                           flags=2)
        vote = {
            1:0,
            2:0,
            3:0,
            4:0
        }
        for [value] in good:
            x = kp2[value.trainIdx].pt[0]
            if x < x0:
                vote[1]+= 1
            elif x0 < x < x1:
                vote[1] += 2
                vote[2] += 1
            elif x1 < x < x2:
                vote[2] += 2

            elif x2 < x < x3:
                vote[3] += 2
            elif x3 < x < x4:
                vote[3] += 1
                vote[4] += 2
            elif x4 < x:
                vote[4] += 1

        img3 = cv2.drawMatchesKnn(origin, kp1, runners, kp2, good, None, **draw_params)
        return img3,vote


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
        fast_mining = cv2.imread('test.png')
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
        print(len(matches))
        good = []
        for m, n in matches:
            if m.distance < 0.7 * n.distance:
                good.append(m)
        print(good)
        if len(good) >= 1:
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

        if np.equal(self.img[196:198,344:346].all(),mining.all()):
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
            if self.pic[850,430].item(0) == 19 and self.pic[850,490].item(0) == 19:
                return True
            else:
                return False
        else:
            return None

    def check_reward_statue(self):
        if self.pic[190,483].item(0) == 0 and self.pic[180,492].item(0) == 0:
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
        blank = cv2.cvtColor(cv2.imread('pics/blank.png'), cv2.COLOR_RGB2GRAY)
        truth_table = []
        for x in stone_table:
            temp_list = []
            for pic in x:
                pic = cv2.cvtColor(pic, cv2.COLOR_RGB2GRAY)
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

        :param stone:
        :param stone_table:
        :return:
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
                if len(good) >= 5:
                    good_index.append(self.x_y_to_pixel(x,y))
                    # src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
                    # dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
                    # M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
                    # print(len(good),M,len(mask))
                    # draw_params = dict(matchColor=(0, 255, 0),  # draw matches in green color
                    #                    singlePointColor=None,
                    #                    matchesMask=None,  # draw only inliers
                    #                    flags=2)
                    #
                    # img3 = cv2.drawMatches(stone, kp1, pic, kp2, good, None, **draw_params)
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
        if self.check_stone_box_statue() == True:
            for y in range(len(truth_table)):
                for x in range(len(truth_table[y])):
                    if truth_table[y][x] == 1:
                        main_stone = stone_table[y][x]
                        pair = self.compare_stone(main_stone,stone_table)
                        if len(pair)>1 and pair not in pairs:
                            pairs.append(pair)
        return pairs

    def vote_quiz(self):
        main_vote = {1: 0,
                     2: 0,
                     3: 0,
                     4: 0}
        count = 0
        while count <= 50:
            print('run', str(count))
            quiz, vote = self.chekc_quiz_pop()
            # cv2.imwrite('quiz/{}.png'.format(time.time()), quiz)
            for key in vote.keys():
                main_vote[key] += vote[key]

            self.img_refresh()
            count += 1
        v = list(main_vote.values())
        k = list(main_vote.keys())
        print(main_vote)
        ans = k[v.index(max(v))]
        cv2.imwrite('ans/{}-{}.png'.format(ans, main_vote[ans]), self.img)
        return v,ans


class UI_controll(Stone_UI):
    def __init__(self,dnpath = 'C:\ChangZhi2\dnplayer2\\',emulator_name = "1"):
        super(UI_controll,self).__init__(dnpath,emulator_name)
        self.auto_attack = 0
        self.toggle = False
        self.clan_exp = 0
        self.START_TIMER = time.time()
        self.main_locker = 0

    def get_reward(self):
        if self.check_reward_statue():
            print('get reward')
            self.controller.touch(480,190)
            self.controller.touch(70,450)
            self.controller.keyevent("04")
            time.sleep(1)

    def quiz_handler(self):
        button = {            # this pos of quiz ans button
            1: [96, 648],
            2: [213, 648],
            3: [327, 648],
            4: [445, 648]
        }
        print('save quiz')

        v,ans = self.vote_quiz()
        if max(v) > 100:
            self.controller.touch(button[ans][0], button[ans][1])
        elif 100 >= max(v):
            print('vote not enough \n do multi vote')
            multi_vote = {
                2:0,
                3:0
            }
            # multi_vote[ans] += 1
            for i in range(0,5):
                print('multi_run =',i)
                value,ans = self.vote_quiz()
                ans = value.index(max(value[1],value[2]))
                multi_vote[ans+1] += 1

            v = list(multi_vote.values())
            k = list(multi_vote.keys())
            print(multi_vote)
            ans = k[v.index(max(v))]
            print("multi vote ans = {}".format(ans))
            self.controller.touch(button[ans][0], button[ans][1])


    def close_pop_box(self):
        self.img_refresh()
        while self.check_pop_box_statue():
            if self.pic[638,95].item(0) == 19 and self.pic[638,445].item(0  ) == 19:
                self.quiz_handler()
                time.sleep(30)
                self.img_refresh()

            else:
                print('pop')
                time.sleep(10)
                self.controller.keyevent("04")
                time.sleep(1)
                self.img_refresh()
        if self.check_stone_box_statue() is False:
            self.auto_attack = 0
        else:
            self.auto_attack = 1

    def Turn_on_auto_attack(self):
        if self.auto_attack == 0:
            print('Turn on auto attack')
            self.img_refresh()
            time.sleep(1)
            if self.check_stone_box_statue():
                print('Turn off stone box')
                self.controller.touch(495, 710)
            time.sleep(1)
            self.img_refresh()
            time.sleep(1)
            if not self.check_auto_attack_statue():
                print('Turn on')
                self.controller.touch(460, 840)
                time.sleep(1)
                self.auto_attack = 1
            else:
                self.auto_attack = 1


    def Turn_on_stone_box(self):
        self.img_refresh()
        if not self.check_stone_box_statue():
            print('turn on stone box')
            self.controller.touch(495,920)
        time.sleep(1)

    def stone_combine(self):
        self.img_refresh()
        pairs = self.check_stone_pairs()

        if len(pairs) > 0:
            print('stone combine')
            temp_list = []
            for pair in pairs:
                for index, value in enumerate(pair[::-1]):
                    if value not in temp_list and pair[::-1][index - 1] not in temp_list:
                        x1, y1 = value
                        x2, y2 = pair[::-1][index - 1]
                        self.controller.swipe(x1, y1, x2, y2, 200)
                        temp_list.append((x1, y1))
                        temp_list.append((x2, y2))


    def Clan_exp_up(self):
        if self.clan_exp - time.time() > 10800 or self.clan_exp == 0:
            self.controller.touch(388, 234)
            time.sleep(2)
            self.img_refresh()
            if self.check_clan_windows():
                #print(self.pic[590,190])
                #[18, 169, 118]
                if all(self.pic[590, 190] == np.array([18, 169, 118])):
                    self.clan_exp = time.time()
                    self.controller.keyevent("04")
                else:
                    self.clan_exp = time.time()
                    self.controller.touch(190, 590)
                    self.controller.keyevent("04")

    def click_ruby_box(self):
        xy = self.check_ruby_box()
        if xy:
            x,y = xy
            self.controller.touch(x,y)

    def main(self,reboot_timer):
        while 1:
            if self.check_game_active() is True:
                try:
                    ran = random.randint(2, 15)
                    self.img_refresh()
                    if self.check_mining_or_mob() == 'mining':
                        self.close_pop_box()
                        self.Turn_on_auto_attack()
                        # self.Clan_exp_up()
                        self.get_reward()
                        self.click_ruby_box()
                        self.Turn_on_stone_box()
                        self.stone_combine()
                        time.sleep(ran)
                    else:
                        self.close_pop_box()
                        self.Turn_on_auto_attack()
                        # self.Clan_exp_up()
                        self.get_reward()
                        self.click_ruby_box()
                        self.Turn_on_stone_box()
                        # self.stone_combine()
                        time.sleep(ran)
                except Exception as error:
                    print(error)
                    with open('error.txt', 'w+') as errorfile:
                        errorfile.write(str(error))
                    time.sleep(5)
            else:
                while self.check_game_active() is False:
                    self.controller.launch_app('net.supercat.stone')
            self.REBOOT(reboot_timer)


    def REBOOT(self,reboot_time):
        """
        emulator reboot
        :param reboot_time:
        :return:
        """
        if time.time() - self.START_TIMER > int(reboot_time)*60*60:
            self.controller.reboot()
            time.sleep(60)
            while self.check_game_active() is False:
                self.controller.launch_app('net.supercat.stone')
            self.START_TIMER = time.time()







if __name__ =="__main__":
    UI = UI_controll()
    UI.main(999)





import cv2
import numpy as np
import elem
import time
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
        self.temp = 'temp.png'
        self.img_refresh()
        self.screenshot()
        self.img =cv2.imread(self.temp) # img in RGB
        self.pic = cv2.cvtColor(self.img,cv2.COLOR_BGR2HSV) #in HSV

    def screenshot(self):
        con = self.controller
        con.screenshot()
        con.pull_screenshot(file_name=self.temp)

    def img_refresh(self):
        self.screenshot()
        self.img =cv2.imread(self.temp) # img in RGB
        self.pic = cv2.cvtColor(self.img,cv2.COLOR_BGR2HSV) #in HSV


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
        #print(truth_table)
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
                    if m.distance < 0.5 * n.distance:
                        good.append(m)
                if len(good) >= 5:
                    good_index.append(self.x_y_to_pixel(x,y))
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
                        pair= self.compare_stone(main_stone,stone_table)
                        if len(pair)>1 and pair not in pairs:
                            pairs.append(pair)
        return pairs

class UI_controll(Stone_UI):
    def __init__(self,dnpath = 'C:\ChangZhi2\dnplayer2\\',emulator_name = "1"):
        super(UI_controll,self).__init__(dnpath,emulator_name)
        self.auto_attack = 0
        self.toggle = False
        self.clan_exp = 0
        self.START_TIMER = time.time()
    def get_reward(self):
        if self.check_reward_statue():
            print('get reward')
            self.controller.touch(480,190)
            self.controller.touch(70,450)
            self.controller.keyevent("04")
            time.sleep(1)

    def close_pop_box(self):
        self.img_refresh()
        while self.check_pop_box_statue():
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
            for pair in pairs:
                temp_list = []
                for index, value in enumerate(pair[::-1]):
                    if value not in temp_list:
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

    def main(self):
        while 1:
            try:
                self.img_refresh()
                if self.check_mining_or_mob() == 'mining':
                    self.close_pop_box()
                    self.Turn_on_auto_attack()
                    self.Clan_exp_up()
                    self.get_reward()
                    self.click_ruby_box()
                    self.Turn_on_stone_box()
                    self.stone_combine()
                    time.sleep(5)
                else:
                    self.close_pop_box()
                    self.Turn_on_auto_attack()
                    self.Clan_exp_up()
                    self.get_reward()
                    self.click_ruby_box()
                    self.Turn_on_stone_box()
                    # self.stone_combine()
                    time.sleep(5)
            except Exception as error:
                print(error)
                with open('error.txt','w+') as errorfile:
                    errorfile.write(str(error))
                time.sleep(5)


    # def REBOOT(self,reboot_time):
    #     if time.time() - self.START_TIMER > reboot_time:
    #         self.controller.
    # def on_press(self,key):
    #     if key == keyboard.KeyCode(char='p'):
    #         self.toggle = not self.toggle
    #
    #         if self.toggle is True:
    #             print('pause')
    #         else:
    #             print('Unpause')
if __name__ =="__main__":
    UI = UI_controll()

    UI.check_stone_pairs()
    # with keyboard.Listener(on_press=UI.on_press)as listener:
    #     listener.join()






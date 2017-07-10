from UIsync import Stone_UI
import logging
import time
import random
import numpy as np

class UI_controll(Stone_UI):

    def __init__(self,dnpath = 'C:\ChangZhi2\dnplayer2\\',emulator_name = "1",ad=False):
        super(UI_controll,self).__init__(dnpath,emulator_name,ad=ad)
        self.auto_attack = 0
        self.toggle = False
        self.clan_exp = 0
        self.START_TIMER = time.time()
        self.main_locker = 0
        self.buster = 0

    def get_reward(self):
        if self.check_reward_statue():
            logging.info('get reward.')
            if self.ad is True:
                self.controller.touch(480,100)
            else:
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
        v,ans = self.vote_quiz()
        std = np.std(v)
        m = max(v)
        mean = np.mean(v)
        logging.info('First solve got std = {},mean = {}'.format(std,mean))

        if std >= 70:
            logging.info('Touch answer {} ,std = {} ,mean = {}'.format(ans,std,mean))
            self.controller.touch(button[ans][0], button[ans][1])
        else:
            self.controller.kill_app('net.supercat.stone')
        # elif 20> std > 10 :
        #     logging.info('Because std is not enough,Doing multi-run.')
        #     multi_vote = {
        #         1:0,
        #         2:0,
        #         3:0,
        #         4:0
        #     }
        #     # multi_vote[ans] += 1
        #     for i in range(0,5):
        #         logging.info('Run = {}'.format(i+1))
        #         value,ans = self.vote_quiz()
        #         multi_vote[ans] += 1
        #
        #     v = list(multi_vote.values())
        #     k = list(multi_vote.keys())
        #     print(multi_vote)
        #     ans = k[v.index(max(v))]
        #     print("multi vote ans = {}".format(ans))
        #     self.controller.touch(button[ans][0], button[ans][1])
        # else:
        #     print('need human detect')

    def close_pop_box(self,solve_quiz = True):
        self.img_refresh()
        count = 0
        while self.check_pop_box_statue() and self.check_game_active():
            count += 1
            if self.pic[638,95].item(0) == 19 and self.pic[638,445].item(0) == 19 and solve_quiz is True:
                logging.info('There is a Quiz,Solving......')
                self.quiz_handler()
                time.sleep(10)
                self.img_refresh()

            else:
                logging.info('There are something pop.')
                time.sleep(10)
                self.controller.keyevent("04")
                time.sleep(1)
                self.img_refresh()
            if count > 10:
                self.controller.kill_app('net.supercat.stone')
                break
        if self.check_stone_box_statue() is False:
            self.auto_attack = 0

    def Turn_on_auto_attack(self):
        if self.auto_attack == 0:
            self.img_refresh()
            time.sleep(1)
            if self.check_stone_box_statue():
                logging.info('checking Auto attack statue')
                self.controller.touch(495, 710)
            time.sleep(1)
            self.img_refresh()
            time.sleep(1)
            if not self.check_auto_attack_statue():
                logging.info('Touch Auto attack button.')
                while not self.check_auto_attack_statue():
                    self.controller.touch(460, 840)
                    time.sleep(1)
                    self.img_refresh()
                self.auto_attack = 1
            else:
                logging.info('Auto attack seems was ON.')
                self.auto_attack = 1

    def Turn_on_stone_box(self):
        logging.info('check stone box.')
        self.img_refresh()
        if not self.check_stone_box_statue():
            logging.info('Keep stone box ON.')
            self.controller.touch(495,920)
        time.sleep(1)

    def stone_combine(self):
        self.img_refresh()
        pairs = self.check_stone_pairs()

        if len(pairs) > 0:
            temp_list = []
            loggingstring = 'combining.'
            for pair in pairs:
                logging.info(loggingstring)
                for index, value in enumerate(pair[::-1]):
                    if value not in temp_list and pair[::-1][index - 1] not in temp_list:
                        x1, y1 = value
                        x2, y2 = pair[::-1][index - 1]
                        self.controller.swipe(x1, y1, x2, y2, 200)
                        temp_list.append((x1, y1))
                        temp_list.append((x2, y2))
                loggingstring += "."

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
        self.img_refresh()
        xy = self.check_ruby_box()
        if xy:
            x,y = xy
            self.controller.touch(x,y)

    def click_fast_mining_one(self):
        self.img_refresh()
        xy = self.check_fast_mining()
        if xy:
            x,y = xy
            self.controller.touch(x,y)
            time.sleep(1)
            self.img_refresh()
            if self.check_Alert_box():
                self.controller.touch(200,565)
                return True
            else:
                return False
    def click_bonus_ruby(self):
        self.img_refresh()
        xy = self.check_bonus_ruby()
        if xy:
            x, y = xy
            self.controller.touch(x, y)
            time.sleep(1)
            self.controller.touch(200, 565)
            if self.pic[638, 95].item(0) == 19 and self.pic[638, 445].item(0) == 19:
                self.img_refresh()
                self.quiz_handler()
                self.img_refresh()
            if self.ad is False:
                time.sleep(40)
                self.controller.keyevent("04")
                time.sleep(1)


    def main(self,reboot_timer,always_fast_mining = False,ran_min = 2,ran_max = 15):
        fast_mining_time = 0
        logging.info('bot start with setting - always_fast_mining = {} , ad_remove = {}'.format(str(always_fast_mining), str(self.ad)))

        while 1:
            try:
                active = self.check_game_active()
                if active is True:
                    self.img_refresh()
                    if self.check_mining_or_mob() == 'mining':
                        logging.info('bot is doing mining thread.')
                        if self.check_rain() is True or always_fast_mining is True:
                            self.buster = 1
                            if time.time() - fast_mining_time > 180:
                                logging.info('bot try to click fasting mining.')
                                if self.click_fast_mining_one():
                                    fast_mining_time = time.time()
                        else:
                            self.buster = 0
                        if self.buster == 0:
                            ran = random.randint(ran_min, ran_max)
                        else:
                            if always_fast_mining is True:
                                ran = random.randint(ran_min,ran_max)
                            else:
                                ran = 1
                        logging.info('sleeping {} sec this run.'.format(ran))
                        self.close_pop_box()
                        self.Turn_on_auto_attack()
                        # self.Clan_exp_up()
                        self.get_reward()
                        self.click_ruby_box()
                        # self.click_bonus_ruby()
                        self.Turn_on_stone_box()
                        self.stone_combine()
                        time.sleep(ran)
                    else:
                        logging.info('bot is doing mob thread.')
                        ran = random.randint(2, 15)
                        logging.info('sleeping {} sec this run.'.format(ran))
                        self.close_pop_box()
                        self.Turn_on_auto_attack()
                        # self.Clan_exp_up()
                        self.get_reward()
                        self.click_ruby_box()
                        # self.click_bonus_ruby()
                        self.Turn_on_stone_box()
                        # self.stone_combine()
                        time.sleep(ran)

                elif active is None:
                    logging.info('emulator seems not exist or crashed,Reboot')
                    self.controller.reboot()
                    time.sleep(15)
                else:
                    loggingstring = 'Open Game.'
                    while self.check_game_active() is False:
                        logging.info(loggingstring)
                        self.controller.launch_app('net.supercat.stone')
                        time.sleep(20)
                        loggingstring += "."

                self.REBOOT(reboot_timer)
            except TimeoutError:
                self.controller.reboot()
                time.sleep(15)
            except Exception as error:
                logging.error(error)
                with open('error.txt', 'w+') as errorfile:
                        errorfile.write(str(error))
                        time.sleep(5)

    def REBOOT(self,reboot_time):
        """
        emulator reboot
        :param reboot_time:
        :return:
        """
        if time.time() - self.START_TIMER > int(reboot_time)*60*60:
            logging.info('Because Reboot timer is out, Rebooting...')
            self.controller.reboot()
            logging.info('Sleeping 60 sec.....')
            time.sleep(60)
            loggingstring = 'Open Game.'
            while self.check_game_active() is False:
                logging.info(loggingstring)
                self.controller.launch_app('net.supercat.stone')
                loggingstring += "."
                time.sleep(15)
            self.START_TIMER = time.time()






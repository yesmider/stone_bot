from UIsync import Stone_UI
import logging
import time
import random
import numpy as np

class UI_controll(Stone_UI):

    def __init__(self,dnpath = 'C:\ChangZhi2\dnplayer2\\',emulator_name = "1",ad=False,adb_mode=False):
        super(UI_controll,self).__init__(dnpath,emulator_name,ad=ad,adb_mode=adb_mode)
        self.auto_attack = 0
        self.toggle = False
        self.clan_exp = 0
        self.START_TIMER = time.time()
        self.main_locker = 0
        self.buster = 0
        self.bonus_ruby_time = 0
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
        # m = max(v)
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
                pair.sort(key=lambda k:k[1] , reverse=True)
                # print(pair)
                for index, value in enumerate(pair):
                    if value not in temp_list and pair[index - 1] not in temp_list:
                        x1, y1 = value
                        x2, y2 = pair[index - 1]
                        # print(x1,y1,x2,y2,index)
                        self.controller.swipe(x1, y1, x2, y2, 250)
                        temp_list.append((x1, y1))
                        temp_list.append((x2, y2))
                loggingstring += "."


    def click_ruby_box(self):
        self.img_refresh()
        xy = self.check_ruby_box()
        if xy:
            x,y = xy
            logging.info('bot click ruby box.')
            self.controller.touch(x,y)

    def click_fast_mining_one(self,level=1):
        self.img_refresh()
        xy = self.check_fast_mining()
        if xy:
            logging.info('bot try to click fast mining.')
            x,y = xy
            self.controller.touch(x,y)
            time.sleep(1)
            self.img_refresh()
            if self.check_Alert_box():
                if level > self.check_mining_text():
                    self.controller.touch(200,565)
                    return True
                else:
                    self.controller.keyevent('4')
                    return None
            else:
                return False
        else:
            return False

    def click_bonus_ruby(self):
        self.img_refresh()
        xy = self.check_bonus_ruby()
        if xy and time.time() - self.bonus_ruby_time > 3600:
            x, y = xy
            logging.info('bot click bonus ruby.')
            self.controller.touch(x, y)
            time.sleep(1)
            self.controller.touch(200, 565)
            time.sleep(2)
            self.img_refresh()
            time.sleep(1)
            if self.pic[638, 95].item(0) == 19 and self.pic[638, 445].item(0) == 19:
                logging.info('quiz pop..')
                self.quiz_handler()
                self.img_refresh()
                time.sleep(1)
            if self.ad is False:
                # print(self.check_Alert_box())
                if self.check_Alert_box():
                    logging.info('ad seems stock out, check after 1hr.')
                    self.bonus_ruby_time = time.time()
                    self.controller.keyevent("04")
                else:
                    logging.info('watching...ads. sleep for 40 sec.')
                    time.sleep(40)
                    logging.info('send return EVENT.')
                    self.controller.keyevent("04")
                    time.sleep(1)


    def main(self,reboot_timer,always_fast_mining = False,ran_min = 2,ran_max = 15,mining_level = 1):
        fast_mining_time = 0
        self.run = 1
        logging.info('bot start with setting - always_fast_mining = {} , ad_remove = {},mining_level = {}'
                     ''.format(str(always_fast_mining), str(self.ad),str(mining_level)))
        if mining_level < 1:
            logging.info('your mining_level setting will disable the weather detection or always fast mining effect.')
        while self.run:

            try:
                active = self.check_game_active()
                if active is True:
                    self.img_refresh()
                    if self.check_mining_or_mob() == 'mining':
                        logging.info('bot is doing mining thread.')
                        if mining_level > 0 and (self.check_rain() is True or always_fast_mining is True):
                            self.buster = 1
                            if time.time() - fast_mining_time > 180:
                                logging.info('bot try to click fasting mining.')
                                res = self.click_fast_mining_one(level=mining_level)
                                # print(res)
                                if res is True:
                                    fast_mining_time = time.time()
                                elif res is None:
                                    logging.info('mining level is {},but we detect now level more than set'
                                                 ',check after 180 sec.'.format(mining_level))
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
                        self.get_reward()
                        self.click_ruby_box()
                        self.click_bonus_ruby()
                        self.Turn_on_stone_box()
                        self.stone_combine()
                        time.sleep(ran)
                    else:
                        logging.info('bot is doing mob thread.')
                        ran = random.randint(2, 15)
                        logging.info('sleeping {} sec this run.'.format(ran))
                        self.close_pop_box()
                        self.Turn_on_auto_attack()
                        self.get_reward()
                        self.click_ruby_box()
                        self.click_bonus_ruby()
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
        return 0
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

    def exit(self):
        self.run = 0




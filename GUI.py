from PyQt5.QtWidgets import QWidget,QApplication,QFileDialog
from PyQt5 import QtCore
from stone_bot import Ui_Stone
import sys
from UIcontrol import UI_controll
import logging
import configparser
# import for pyinstaller build
import PyQt5.uic.pyuic

class QtHandler(logging.Handler,QtCore.QObject):
    signal = QtCore.pyqtSignal(str)
    def __init__(self):
        logging.Handler.__init__(self)
        QtCore.QObject.__init__(self)
    @QtCore.pyqtSlot()
    def emit(self, record):
        msg = self.format(record)
        self.signal.emit(msg)



class UI(QWidget,Ui_Stone):
        def __init__(self):
            super(UI,self).__init__()
            self.setupUi(self)
            #read config
            self.read_config()

            #set setting value
            self.dir_string.setText(self.config_path)
            self.emu_name.setText(self.config_name)
            self.ad_remove_checker.setChecked(self.config_ad_remove)
            self.restart_timer.setValue(self.config_reboot_timer)
            self.DEBUG.setChecked(self.config_DEBUG)
            self.always_fast_mining_checker.setChecked(self.config_fast_mining)
            self.max_sleep_box.setValue(self.config_max_sleep_time)
            self.max_sleep_box.setMinimum(self.config_min_sleep_time)
            self.min_sleep_box.setValue(self.config_min_sleep_time)
            self.min_sleep_box.setMaximum(self.config_max_sleep_time)
            self.mining_level.setValue(self.config_mining_level)
            #init python log handler
            self.loghandler = QtHandler()
            self.loghandler.setFormatter(logging.Formatter('%(asctime)s %(funcName)s %(message)s'))
            logging.getLogger().addHandler(self.loghandler)
            if self.config_DEBUG is True:
                logging.getLogger().setLevel(logging.DEBUG)
            else:
                logging.getLogger().setLevel(logging.INFO)
            self.loghandler.signal.connect(self.print_log)

            #init bot class


            #start thread
            self.main_thread = Worker(self.main,())
            #connect
            self.startbutton.clicked.connect(self.push_start)
            self.pausebutton.clicked.connect(self.push_pause)
            self.save_setting.clicked.connect(self.save)
            #
            self.DEBUG.clicked.connect(self.debug)
            self.ad_remove_checker.clicked.connect(self.ad_remove_handler)
            self.always_fast_mining_checker.clicked.connect(self.fast_mining_handler)
            #
            self.restart_timer.valueChanged.connect(self.restart_handler)
            self.max_sleep_box.valueChanged.connect(self.max_sleep_handler)
            self.min_sleep_box.valueChanged.connect(self.min_sleep_handler)
            self.mining_level.valueChanged.connect(self.mining_level_handler)
            #
            self.dir_string.textChanged.connect(self.dir_string_handler)
            self.dir.clicked.connect(self.push_dir)
            #
            self.emu_name.textChanged.connect(self.emu_name_handler)

        def read_config(self):
            self.config = configparser.ConfigParser()
            # config file decoding
            try:
                self.config.read('config.ini')
            except UnicodeDecodeError:
                try:
                    self.config.read('config.ini', encoding='UTF-8')
                except configparser.MissingSectionHeaderError:
                    self.config.read('config.ini', encoding='UTF-8-SIG')
            self.config_name = self.config['config']['emulator_name']
            self.config_path = self.config['config']['emulator_path']
            self.config_reboot_timer = int(self.config['config']['reboot_timer'])
            self.config_ad_remove = self.config.getboolean('config', 'ad_remove')
            self.config_DEBUG = self.config.getboolean('config','DEBUG')
            self.config_fast_mining = self.config.getboolean('config','always_fast_mining')
            self.config_max_sleep_time = int(self.config['config']['max_sleep'])
            self.config_min_sleep_time = int(self.config['config']['min_sleep'])
            self.config_mining_level = int(self.config['config']['mining_level'])
            # if self.config_path[-1] is not "\\":
            #     self.config_path += "\\"
            #     self.config['config']['emulator_path'] = self.config_path
            #     with open('config.ini', 'w') as configfile:
            #         self.config.write(configfile)
        #
        def enable_setting_group(self):
            self.startbutton.setEnabled(True)
            self.ad_remove_checker.setEnabled(True)
            self.dir_string.setEnabled(True)
            self.restart_timer.setEnabled(True)
            self.emu_name.setEnabled(True)
            self.dir.setEnabled(True)
            if self.config_mining_level > 0:
                self.always_fast_mining_checker.setEnabled(True)
            self.max_sleep_box.setEnabled(True)
            self.min_sleep_box.setEnabled(True)
            self.mining_level.setEnabled(True)
        def disable_setting_group(self):
            self.startbutton.setEnabled(False)
            self.ad_remove_checker.setEnabled(False)
            self.dir_string.setEnabled(False)
            self.restart_timer.setEnabled(False)
            self.emu_name.setEnabled(False)
            self.dir.setEnabled(False)
            self.always_fast_mining_checker.setEnabled(False)
            self.max_sleep_box.setEnabled(False)
            self.min_sleep_box.setEnabled(False)
            self.mining_level.setEnabled(False)
        @QtCore.pyqtSlot()
        def push_start(self):
            self.logtext.appendPlainText('------------START------------')
            self.main_thread.start()
            self.disable_setting_group()

        @QtCore.pyqtSlot()
        def push_pause(self):
            self.logtext.appendPlainText('------------PAUSE------------')
            self.main_thread.terminate()
            self.enable_setting_group()

        @QtCore.pyqtSlot()
        def push_dir(self):
            dir = QFileDialog.getExistingDirectory(self,'path')
            if dir != '':
                self.config['config']['emulator_path'] = dir
                self.config_path = self.config['config']['emulator_path']
                self.dir_string.setText(dir)

        @QtCore.pyqtSlot()
        def save(self):
            with open('config.ini','w') as configfile:
                self.config.write(configfile)
        #
        @QtCore.pyqtSlot(str)
        def print_log(self,msg):
            self.logtext.appendPlainText(msg)

        @QtCore.pyqtSlot()
        def main(self):
            try:
                self.bot = UI_controll(self.config_path,self.config_name,ad=self.config_ad_remove,adb_mode=self.adb_test_checkBox.isChecked())
                self.bot.main(self.config_reboot_timer,always_fast_mining=self.config_fast_mining,
                              ran_max=self.config_max_sleep_time,ran_min=self.config_min_sleep_time,mining_level=self.config_mining_level)

            except Exception as exc:
                logging.warning(exc)
                self.enable_setting_group()


        @QtCore.pyqtSlot()
        def debug(self):
            if self.DEBUG.checkState():
                self.config['config']['DEBUG'] = 'True'

                logging.getLogger().setLevel(logging.DEBUG)
            else:
                self.config['config']['DEBUG'] = 'False'
                logging.getLogger().setLevel(logging.INFO)

            self.config_DEBUG = self.config.getboolean('config', 'DEBUG')

        @QtCore.pyqtSlot()
        def ad_remove_handler(self):
            if self.ad_remove_checker.checkState():
                self.config['config']['ad_remove'] = 'True'
            else:
                self.config['config']['ad_remove'] = 'False'

            self.config_ad_remove = self.config.getboolean('config', 'ad_remove')

        @QtCore.pyqtSlot(int)
        def restart_handler(self,value):
            self.config['config']['reboot_timer'] = str(value)
            self.config_reboot_timer = int(self.config['config']['reboot_timer'])

        @QtCore.pyqtSlot(str)
        def dir_string_handler(self,string):
            self.config['config']['emulator_path'] = string
            self.config_path = self.config['config']['emulator_path']

        @QtCore.pyqtSlot(str)
        def emu_name_handler(self,string):
            self.config['config']['emulator_name'] = string
            self.config_name = self.config['config']['emulator_name']

        @QtCore.pyqtSlot()
        def fast_mining_handler(self):
            if self.always_fast_mining_checker.checkState():
                self.config['config']['always_fast_mining'] = 'True'
            else:
                self.config['config']['always_fast_mining'] = 'False'
            self.config_fast_mining = self.config.getboolean('config','always_fast_mining')

        @QtCore.pyqtSlot(int)
        def max_sleep_handler(self,value):
            self.config['config']['max_sleep'] = str(value)
            self.config_max_sleep_time = int(self.config['config']['max_sleep'])
            self.min_sleep_box.setMaximum(self.config_max_sleep_time)

        @QtCore.pyqtSlot(int)
        def min_sleep_handler(self,value):
            self.config['config']['min_sleep'] = str(value)
            self.config_min_sleep_time = int(self.config['config']['min_sleep'])
            self.max_sleep_box.setMinimum(self.config_min_sleep_time)
        def mining_level_handler(self,value):
            self.config['config']['mining_level'] = str(value)
            self.config_mining_level = int(self.config['config']['mining_level'])
            if value == 0:
                self.always_fast_mining_checker.setEnabled(False)
            else:
                self.always_fast_mining_checker.setEnabled(True)
        def closeEvent(self, QCloseEvent):
            self.save()

class Worker(QtCore.QThread):
    def __init__(self, func, args):
        super(Worker, self).__init__()
        self.func = func
        self.args = args

    def run(self):
        self.func(*self.args)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    windows = UI()
    windows.show()
    sys.exit(app.exec())
import configparser
import UIcontrol
import os
import logging
config = configparser.ConfigParser()
# config file decoding
# todo check img shape
logging.basicConfig(format='%(asctime)s %(funcName)s %(message)s',level='DEBUG')
try:
    config.read('config.ini')
except UnicodeDecodeError:
    try:
        config.read('config.ini',encoding='UTF-8')
    except configparser.MissingSectionHeaderError:
        config.read('config.ini',encoding='UTF-8-SIG')
name = config['config']['emulator_name']
path = config['config']['emulator_path']
reboot_timer = config['config']['reboot_timer']
ad_remove = config.getboolean('config','ad_remove')
if path[-1] is not "\\":
    path += "\\"
    config['config']['emulator_path'] = path
    with open('config.ini','w') as configfile:
        config.write(configfile)

# main thread
MODE = 1
UI = UIcontrol.UI_controll(path,name)
UI.main(reboot_timer,ad_remove)
# # try:
#     UI = UIcontrol.UI_controll(path,name)
#     if MODE == 1:
#         UI.main(reboot_timer,ad_remove)
#
# # except Exception as exc:
# #     print(exc)
# #     os.system('pause')
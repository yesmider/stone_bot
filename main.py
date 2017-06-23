import configparser
import UIsync
import os
config = configparser.ConfigParser()
# config file decoding
# todo check img shape
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
ad_remove = config['config']['ad_remove']
if path[-1] is not "\\":
    path += "\\"
    config['config']['emulator_path'] = path
    with open('config.ini','w') as configfile:
        config.write(configfile)

# main thread
try:
    UI = UIsync.UI_controll(path,name)
    UI.main(reboot_timer,ad_remove)
except Exception as exc:
    print(exc)
    os.system('pause')
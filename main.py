import configparser
import UIsync
# todo emulator restart
config = configparser.ConfigParser()
try:
    config.read('config.ini')
except UnicodeDecodeError:
    try:
        config.read('config.ini',encoding='UTF-8')
    except configparser.MissingSectionHeaderError:
        config.read('config.ini',encoding='UTF-8-SIG')
name = config['config']['emulator_name']
path = config['config']['emulator_path']
if path[-1] is not "\\":
    path += "\\"
    config['config']['emulator_path'] = path
    with open('config.ini','w') as configfile:
        config.write(configfile)

UI = UIsync.UI_controll(path,name)
UI.main()

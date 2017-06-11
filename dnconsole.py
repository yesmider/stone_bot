import subprocess
import time
import logging
logging.basicConfig(format='%(asctime)s %(funcName)s %(message)s',level='INFO')
class dn:
    def __init__(self,path):
        self.root = path+"dnconsole.exe "
    def quit(self,method,n):

        command = self.root+"quit "+"--"+method+" "+str(n)
        if method == "name" or method == "index":
            logging.info('quitting emulator {} by {}'.format(n, method))
            ret = subprocess.check_output(command)
            if ret != b"":
                raise Exception(str(ret))
        else:
             raise Exception("method not support")


    def quitall(self):
        command = self.root+"quitall "
        logging.info('quitting all emulators')
        opt = subprocess.check_output(command)
        if opt != b'':
            raise Exception(opt)
        else:
             raise Exception("method not support")
    def launch(self,method,n):
        command = self.root +"launch "+"--"+method+" "+str(n)
        if method =="name" or method == "index":
            logging.info('launch emulator {} by {}'.format(n, method))
            opt = subprocess.check_output(command)
            if opt != b"":
                raise Exception(opt)
        else:
             raise Exception("method not support")

    def reboot(self, method, n):
        command = self.root + "reboot "+"--"+method+" "+str(n)
        if method == "name" or method == "index":
            logging.info('reboot all emulators')
            opt = subprocess.check_output(command)
            if opt != b"":
                raise Exception(opt)
        else:
             raise Exception("method not support")
    def runapp(self, method, n, apk_name):
        command = self.root + "runapp "+"--"+method+" "+str(n)+" --packagename "+apk_name
        if method == "index" or method == "name":
            logging.info('runapp {} on emulator {} by {} method'.format(apk_name,n, method))
            opt = subprocess.check_output(command)
            if opt != b"":
                raise Exception(opt)
        else:
            raise Exception("method not support")
    def adb(self, method, n, cmd):
        command = self.root + "adb "+"--"+method+" "+str(n)+" --command "+ '"'+cmd+'"'
        #print(cmd)
        if method == "index" or method == "name":
            logging.info('emulator {} by method {} - {}'.format(n,method,cmd))
            opt = subprocess.check_output(command)
            logging.info('call back : {}'.format(opt))
            return opt
        else:
            raise Exception("method not support")

    def isrunning(self,method,n):
        command = self.root +"isrunning "+ "--"+method+" "+ str(n)
        if method == "index" or method == "name":
            opt = subprocess.check_output(command)
            logging.info('checking emulator {} running statue'.format(n))
            if opt == b'running':
                logging.info('emulator {} is running'.format(n))
                return 1
            elif opt == b'stop':
                logging.info('emulator {} is not running.'.format(n))
                return 0
        else:
            raise Exception("method not support")
    # def list:
    #
    # def runninglist:
    #

    # def list2:
    #
    # def add:
    #
    # def copy:
    #
    # def remove:
    #
    # def modify:
    #
    # def installapp:
    #
    # def uninstallapp:
    #
    # def killapp:
    #
    # def locate:
    #

    # def setprop:
    #
    # def getprop:
    #
    # def downcpu:
    #
    # def backup:
    #
    # def restore:
    #
    # def reset:

if __name__ == "__main__":
    root = "C:\ChangZhi2\dnplayer2\\"
    dd = dn(root)

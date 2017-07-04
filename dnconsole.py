import subprocess
import time
import logging

class dn:
    def __init__(self,path):
        self.root = path+"dnconsole.exe "
    def quit(self,method,n):

        command = self.root+"quit "+"--"+method+" "+str(n)
        if method == "name" or method == "index":
            logging.debug('quitting emulator {} by {}'.format(n, method))
            ret = subprocess.check_output(command)
            if ret != b"":
                raise Exception(str(ret))
        else:
             raise Exception("method not support")


    def quitall(self):
        command = self.root+"quitall "
        logging.debug('quitting all emulators')
        opt = subprocess.check_output(command)
        if opt != b'':
            raise Exception(opt)
        else:
             raise Exception("method not support")
    def launch(self,method,n):
        command = self.root +"launch "+"--"+method+" "+str(n)
        if method =="name" or method == "index":
            logging.debug('launch emulator {} by {}'.format(n, method))
            opt = subprocess.check_output(command)
            if opt != b"":
                raise Exception(opt)
        else:
             raise Exception("method not support")

    def reboot(self, method, n):
        command = self.root + "reboot "+"--"+method+" "+str(n)
        if method == "name" or method == "index":
            logging.debug('reboot all emulators')
            opt = subprocess.check_output(command)
            if opt != b"":
                raise Exception(opt)
        else:
             raise Exception("method not support")
    def runapp(self, method, n, apk_name):
        command = self.root + "runapp "+"--"+method+" "+str(n)+" --packagename "+apk_name
        if method == "index" or method == "name":
            logging.debug('runapp {} on emulator {} by {} method'.format(apk_name,n, method))
            opt = subprocess.check_output(command)
            if opt != b"":
                raise Exception(opt)
        else:
            raise Exception("method not support")
    def adb(self, method, n, cmd,print_call_back = 1):
        command = self.root + "adb "+"--"+method+" "+str(n)+" --command "+ '"'+cmd+'"'
        #print(cmd)
        if method == "index" or method == "name":
            logging.debug('emulator {} by method {} - {}'.format(n,method,cmd))
            try:
                opt = subprocess.check_output(command)
            except subprocess.CalledProcessError as exc:
                opt = exc.stdout
            if print_call_back == 1:
                logging.debug('call back : {}'.format(opt))
            return opt
        else:
            raise Exception("method not support")

    def isrunning(self,method,n):
        command = self.root +"isrunning "+ "--"+method+" "+ str(n)
        if method == "index" or method == "name":
            opt = subprocess.check_output(command)
            logging.debug('checking emulator {} running statue'.format(n))
            if opt == b'running':
                logging.debug('emulator {} is running'.format(n))
                return True
            elif opt == b'stop':
                logging.debug('emulator {} is not running.'.format(n))
                return False
        else:
            raise Exception("method not support")

    def killapp(self,method,n,apk_name):
        command = self.root +"killapp "+"--"+method+" "+str(n)+" --packagename "+apk_name
        if method == 'index' or method == 'name':
            opt = subprocess.check_output(command)
            logging.debug('killapp {} on emulator {} by {} method'.format(apk_name, n, method))
            if opt != b"":
                raise Exception(opt)
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

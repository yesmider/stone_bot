import get_console_opt
import os
import logging
# logging.basicConfig(format='%(asctime)s %(funcName)s %(message)s',level='DEBUG')
class dn:
    def __init__(self,path):
        self.root = os.path.join(path,"dnconsole.exe")+' '
        if not os.path.isfile(self.root):
            raise LookupError('dnconsole not found. change your emulator path')
    def quit(self,method,n):

        command = self.root+"quit "+"--"+method+" "+str(n)
        if method == "name" or method == "index":
            logging.debug('quitting emulator {} by {}'.format(n, method))
            opt,err = get_console_opt.get_console_output(command)
            if err != "":
                raise Exception(str(err))
        else:
             raise Exception("method not support")


    def quitall(self):
        command = self.root+"quitall "
        logging.debug('quitting all emulators')
        opt,err = get_console_opt.get_console_output(command)
        if opt != '':
            raise Exception(opt)
        else:
             raise Exception("method not support")
    def launch(self,method,n):
        command = self.root +"launch "+"--"+method+" "+str(n)
        if method =="name" or method == "index":
            logging.debug('launch emulator {} by {}'.format(n, method))
            opt,err = get_console_opt.get_console_output(command)
            if opt != "":
                raise Exception(opt)
        else:
             raise Exception("method not support")

    def reboot(self, method, n):
        command = self.root + "reboot "+"--"+method+" "+str(n)
        if method == "name" or method == "index":
            logging.debug('reboot all emulators')
            opt,err = get_console_opt.get_console_output(command)
            if opt != "":
                raise Exception(opt)
        else:
             raise Exception("method not support")
    def runapp(self, method, n, apk_name):
        command = self.root + "runapp "+"--"+method+" "+str(n)+" --packagename "+apk_name
        if method == "index" or method == "name":
            logging.debug('runapp {} on emulator {} by {} method'.format(apk_name,n, method))
            opt,err = get_console_opt.get_console_output(command)
            if opt != "":
                raise Exception(opt)
        else:
            raise Exception("method not support")
    def adb(self, method, n, cmd,print_call_back = 1):
        command = self.root + "adb "+"--"+method+" "+str(n)+" --command "+ '"'+cmd+'"'
        #print(cmd)
        if method == "index" or method == "name":
            logging.debug('emulator {} by method {} - {}'.format(n,method,cmd))
            opt,err = get_console_opt.get_console_output(command)
            # print('opt',opt,err)
            opt = opt.replace('\n', "")
            opt = opt.replace('\r', '')
            if print_call_back == 1 and opt != '':
                logging.debug('call back : {}'.format(opt))
            return opt
        else:
            raise Exception("method not support")

    def isrunning(self,method,n):
        command = self.root +"isrunning "+ "--"+method+" "+ str(n)
        if method == "index" or method == "name":
            opt,err = get_console_opt.get_console_output(command)

            logging.debug('checking emulator {} running statue'.format(n))
            if opt == 'running':
                logging.debug('emulator {} is running'.format(n))
                return True
            elif opt == 'stop':
                logging.debug('emulator {} is not running.'.format(n))
                return False
        else:
            raise Exception("method not support")

    def killapp(self,method,n,apk_name):
        command = self.root +"killapp "+"--"+method+" "+str(n)+" --packagename "+apk_name
        if method == 'index' or method == 'name':
            opt = get_console_opt.get_console_output(command)
            logging.debug('killapp {} on emulator {} by {} method'.format(apk_name, n, method))
            if opt != "":
                raise Exception(opt)
            else:
                raise Exception("kill app done.")
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
    dd.isrunning('name',1)

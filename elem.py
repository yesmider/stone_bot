import xml.etree.ElementTree as ET
import re
import tempfile
import dnconsole
import time
class Element:
    def __init__(self,path,name):
        self.device = name
        self.dn = dnconsole.dn(path)
        self.filedir = tempfile.gettempdir()+"\\uidump.xml"
        self.pattern = re.compile(r"\d+")
    def __uidump(self):
        #self.dn.adb("name",self.device,"wait-for-device ")
        self.dn.adb("name",self.device,"shell uiautomator dump /data/local/tmp/uidump.xml")
        self.dn.adb("name",self.device,"pull /data/local/tmp/uidump.xml " + self.filedir)

    def __element(self,attrib,name):
        self.__uidump()
        tree = ET.parse(self.filedir)
        root = tree.iter("node")
        for elem in root:
            if elem.attrib[attrib] == name:
                bounds = elem.attrib["bounds"]
                coord = self.pattern.findall(bounds)
                Xpoint = (int(coord[2]) - int(coord[0])) / 2.0 + int(coord[0])
                Ypoint = (int(coord[3]) - int(coord[1])) / 2.0 + int(coord[1])
                return Xpoint,Ypoint

    def __elements(self,attrib,name):
        self.__uidump()
        tree = ET.parse(self.filedir)
        root = tree.iter("node")
        for elem in root:
            if elem.attrib[attrib]==name:
                bounds = elem.attrib["bounds"]
                coord = self.pattern.findall(bounds)
                Xpoint = (int(coord[2]) - int(coord[0])) / 2.0 + int(coord[0])
                Ypoint = (int(coord[3]) - int(coord[1])) / 2.0 + int(coord[1])
                list.append((Xpoint,Ypoint))
        return list


    def findElementByName(self, name):
        return self.__element("text", name)

    def findElementsByName(self, name):
        return self.__elements("text", name)

    def findElementByClass(self, className):
        return self.__element("class", className)

    def findElementsByClass(self, className):
        return self.__elements("class", className)

    def findElementById(self, id):
        return self.__element("resource-id",id)

    def findElementsById(self, id):
        return self.__elements("resource-id",id)

    def touch(self,x,y):
        #self.dn.adb('name', self.device, 'wait-for-device')
        self.dn.adb("name",self.device," shell input tap "+str(x)+" "+str(y))
    def screenshot(self):
        #self.dn.adb('name', self.device, 'wait-for-device')
        self.dn.adb("name",self.device,"shell screencap -p /sdcard/temp.png")
    def pull(self,filename):
        #self.dn.adb('name', self.device, 'wait-for-device')
        self.dn.adb("name",self.device,'pull /sdcard/temp.png {0}.png'.format(filename))

class controller(Element):
    def __init__(self,path,name):
        super(controller,self).__init__(path,name)

    def screenshot(self,filepath = '/sdcard/temp.png'):
        # self.dn.adb('name', self.device, 'wait-for-device')
        self.dn.adb("name",self.device,"shell screencap -p {}".format(filepath))


    def pull(self,targetfile,filename):
        # self.dn.adb('name', self.device, 'wait-for-device')
        self.dn.adb("name",self.device,'pull {} {}'.format(targetfile,filename))

    def pull_screenshot(self,target_file = '/sdcard/temp.png',file_name = 'temp.png'):
        self.dn.adb("name", self.device, 'pull {} {}'.format(target_file, file_name))

    def swipe(self,x1,y1,x2,y2,duration):
        # self.dn.adb('name', self.device, 'wait-for-device')
        self.dn.adb("name",self.device,'shell input swipe {} {} {} {} {}'.format(x1,y1,x2,y2,duration))

    def keyevent(self,key):
        # self.dn.adb('name',self.device, 'wait-for-device')
        self.dn.adb("name",self.device,'shell input keyevent {}'.format(key))

    def get_now_activity_windows(self):
        while self.dn.isrunning('name',self.device) is False:
            time.sleep(20)
        p = re.compile(r"mSurface=Surface\(name=[a-zA-Z0-9\.]+/[a-zA-Z0-9\.]+")
        call_back = str(self.dn.adb('name',self.device,' shell dumpsys window windows',print_call_back=0))
        name = p.findall(call_back)
        if len(name) >0:
            name = name[0].replace('mSurface=Surface(name=','')
            return name
        else:
            return None
    def reboot(self):
        self.dn.reboot('name',self.device)

    def launch_app(self,apk):
        self.dn.runapp('name',self.device,apk)

    def kill_app(self,apk):
        self.dn.killapp('name',self.device,apk)

    def get_port_by_name(self,name):
        emulator_list = self.dn.list2()
        index = emulator_list[name]
        port = int(index)*2+5555
        return port





if __name__ == "__main__":
    root = "C:\ChangZhi2\dnplayer2\\"





import get_console_opt
import cv2
import numpy as np

path = 'C:\ChangZhi2\dnplayer2\\adb.exe'
def adb_screen_cap(target_port):
    popen= get_console_opt.open_console_output('{} -s 127.0.0.1:{} shell screencap -p'.format(path,str(target_port)))
    out,err = popen.communicate(timeout=15)
    out = out.replace(b'\x0D\x0A',b'\x0A').replace(b'\x0D\x0A',b'\x0A')
    nparr = np.frombuffer(out,np.uint8)
    # print(len(nparr.tolist()))
    img_np = cv2.imdecode(nparr, 1)
    return img_np


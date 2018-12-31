#!/usr/local/bin/python3
# -*- coding:utf-8 -*- 
'''
 * @Author: Aeonni 
 * @Date: 2018-10-10 10:53:15 
 * @Last Modified by:   Aeonni 
 * @Last Modified time: 2018-10-10 10:53:15 
 * @Blog: https://www.aeonni.com 
 * @Desc: 
'''

__version__ = '1.0.1'
moduleName = 'Camera'

print('loading...Device_Cam ver. ', __version__)

from picamera import PiCamera
from picamera.array import PiRGBArray
from Modules.Aeonni_Nixie_Module import AN_Module
import threading
import time
import cv2
import os

face_cascade = cv2.CascadeClassifier('/usr/local/share/OpenCV/haarcascades/haarcascade_frontalface_alt2.xml')


def get_faces( img, path ):

    gray = cv2.cvtColor( img, cv2.COLOR_BGR2GRAY )
    faces = face_cascade.detectMultiScale( gray )

    if len(faces) == 0:
        return None

    for ( x, y, w, h ) in faces:

        cv2.rectangle( img, ( x, y ),( x + w, y + h ), ( 200, 255, 0 ), 2 )
        cv2.putText(img, "Face No." + str( len( faces ) ), ( x, y ), cv2.FONT_HERSHEY_SIMPLEX, 0.5, ( 0, 0, 255 ), 2 )

    cv2.putText(img, "Time : " + time.strftime("%H.%M.%S"), ( 10, 10 ), cv2.FONT_HERSHEY_SIMPLEX, 0.5, ( 0, 0, 255 ), 2 ) 
    cv2.imwrite(path, img)
    return True


class Cam(AN_Module):
    def __init__(self, path):
        AN_Module.__init__(self, moduleName, __version__)
        self.path = path
        self.monitorfile = path+'detect.jpg'
        self.camera = PiCamera()
        self.camera.awb_mode = 'auto'
        self.rawCapture = PiRGBArray( self.camera )
        self.isRecording = False
        self.isMonitoring = False
        self.Sem = threading.Semaphore(1)
    @AN_Module.isRunning
    def capture(self, n = 1, t = 0.1):
        self.camera.resolution = ( 1280, 720 )
        if self.isRecording:
            return None
        tm = time.strftime("%Y_%m_%d%H%M%S")
        imgs = []
        for i in range(n):
            imgs.append(tm+'_%d.jpg'%(i+1))
        r = []
        for each in imgs:
            try:
                path = self.path + each
                time.sleep(t)
                self.Sem.acquire()
                self.camera.capture(output = path)
                self.Sem.release()
                r.append(path)
            except:
                pass
        return r
    def record(self, t):
        self.camera.resolution = ( 1280, 720 )
        if self.isRecording or self.isMonitoring:
            return None
        try:
            tm = time.strftime("%Y_%m_%d%H%M%S")
            f = self.path+tm+'.h264'
            self.Sem.acquire()
            self.isRecording = True
            self.camera.start_recording(f)
            time.sleep(t)
            self.camera.stop_recording()
            self.Sem.release()
            self.isRecording = False
            mpf = self.path+tm+'.mp4'
            os.system('MP4Box -fps 30 -add %s %s'%(f, mpf))
            os.system('rm %s'%f)
            return mpf
        except:
            return None
    def monitor(self, send):
        self.camera.resolution = ( 640, 360 )
        if self.isRecording:
            send['txt']('摄像头正忙')
            return None
        self.Sem.acquire()
        self.isMonitoring = True
        self.camera.capture( self.rawCapture, format="bgr" )
        self.rawCapture.truncate( 0 ) 
        for frame in self.camera.capture_continuous( self.rawCapture, format="bgr", use_video_port=True ):
            image = frame.array
            if get_faces(image, self.monitorfile):
                send['txt']('这里有坏银！')
                send['img'](self.monitorfile)
            self.rawCapture.truncate( 0 )
            if self.isMonitoring == False:
                break
            time.sleep(1)
        self.Sem.release()
        # while self.isMonitoring:
        #     time.sleep(1)
        #     try:
        #         self.Sem.acquire()
        #         self.camera.capture(output = self.monitorfile)
        #         self.Sem.release()
        #         if get_faces(cv2.imread(self.monitorfile), self.monitorfile):
        #             send['txt']('这里有坏银！')
        #             send['img'](self.monitorfile)
        #     except:
        #         pass
            
    def runMonitor(self, cbks):
        threading.Thread(target = self.monitor, args = [cbks]).start()

    def stopMonitor(self):
        self.isMonitoring = False


if __name__ == '__main__':
    c = Cam('/home/pi/Nixie/CamCapture/')
    print(c.capture(n = 5))
    print(c.record(t = 5))
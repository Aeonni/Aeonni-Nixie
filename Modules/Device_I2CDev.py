#!/usr/local/bin/python3
# -*- coding:utf-8 -*- 
'''
 * @Author: Aeonni 
 * @Date: 2018-10-03 09:05:17 
 * @Last Modified by:   Aeonni 
 * @Last Modified time: 2018-10-10 09:05:17 
 * @Blog: https://www.aeonni.com 
 * @Desc: 
'''

__version__ = '0.4.3'
moduleName = 'Arduino-i2c'

print('loading...Device_I2CDev ver. ', __version__)

import smbus
import time
import numpy as np
import threading
from threading import Timer
from multiprocessing import Value
from Modules.Aeonni_Nixie_Module import AN_Module

import random

priority = dict(
    default = -1,
    CLOCK = 1,
    NFC = 10,
    Network = 1,
)

nao = Value('i', -1)

class Arduino(AN_Module):
    def __init__(self, addr):
        self.__version__ = __version__ 
        AN_Module.__init__(self, moduleName, __version__)
        self.state = 'Running'
        self.dev = smbus.SMBus(1)
        self.addr = addr

        self.Sem = threading.Semaphore(1)
        self.PrioSem = threading.Semaphore(1)

        self.dev.write_i2c_block_data(self.addr, 70, list(('F\n').encode('ascii')))
        self.trytime = 5
        self.lastLEDString = 'aaaaaaaa'
        
        self.closeDev('F')
        self.fan_state = 0
        
        self.checkPiTemp()
        self.getDHT11(True)

        # self.incatch = nao
        # print('dev_init!')

    def secure_read(self, addr, length, name = "Default"):
        self.Sem.acquire()
        # print(name, " got the sem!")
        trytime = self.trytime
        while trytime:
            try:
                block = self.dev.read_i2c_block_data(self.addr, addr, length)
                break
            except OSError:
                print('Retry Read: ', length)
                time.sleep(0.05)
                trytime -= 1
        self.Sem.release()
        # print(name, " released the sem!")
        if trytime:
            for i in range(len(block)):
                if block[i] > 128:
                    block = block[:i]
                    break
            return bytes(block).decode('ascii')
        else:
            return 0

    def secure_write(self, addr, li, name = "default"):
        self.Sem.acquire()
        # print(name, " got the sem!")
        trytime = self.trytime
        while trytime:
            try:
                r = self.dev.write_i2c_block_data(self.addr, addr, li)
                break
            except OSError:
                print('Retry write: ', li)
                time.sleep(0.05)
                trytime -= 1
        self.Sem.release()
        # print(name, " released the sem!")
        return trytime
    def writeLED(self, string, name = "default"):
        if self.checkPrio(name):
            string = string.replace(' ', 'd')
            # self.dev.write_i2c_block_data(self.addr, 76, list((string+'\n').encode('ascii')))
            if self.secure_write(76, list((string+'\n').encode('ascii')), name = name):
                self.lastLEDString = string
            time.sleep(0.1)

        # exit()

    def writeNixie(self, string, name = "default"):
        if self.checkPrio(name):
            if '.' in string:
                s1, s2 = self.nixieFormatString(string)
                self.secure_write(78, list((s1[::-1]+'\n').encode('ascii')), name = name)
                # self.dev.write_i2c_block_data(self.addr, 78, list((s1[::-1]+'\n').encode('ascii')))
                time.sleep(0.1)
                self.secure_write(76, list((s2+'\n').encode('ascii')),name = name)
                # self.dev.write_i2c_block_data(self.addr, 76, list((s2+'\n').encode('ascii')))
                time.sleep(0.1)
            else:
                self.secure_write(78, list((string[::-1]+'\n').encode('ascii')), name = name)
                # self.dev.write_i2c_block_data(self.addr, 78, list((string[::-1]+'\n').encode('ascii')))
                time.sleep(0.1)

    def checkPrio(self, name):
        self.PrioSem.acquire()
        t = random.randint(1,9999)
        # print(nao, name, t)
        if priority[name] > nao.value:
            nao.value = priority[name]
            # print(t, '>')
            self.PrioSem.release()
            return True
        elif priority[name] == nao.value:
            # print(t, '=')
            self.PrioSem.release()
            return True
        else:
            # print(t, '<')
            self.PrioSem.release()
        return False

    def resetPrio(self, name):
        if self.checkPrio(name):
            nao.value = -1

    def getDHT11(self, conti = False):
        r = self.secure_read(68, 16, name = 'GETDHT11')
        if r:
            try:
                t, h = float(r[2:6]), float(r[8:12])
                with open('./Data/data_base/dht.csv', 'a') as f:
                    f.write('%d %.1f %.1f\n'%(int(time.time()), t, h))
            except:
                print("ERR: ", r)
                if conti:
                    Timer(60, self.getDHT11, [True]).start()
                return None
            if conti:
                Timer(60, self.getDHT11, [True]).start()
            return t,h
        else:
            if conti:
                Timer(60, self.getDHT11, [True]).start()
            return None
        
    def getState(self):
        return self.secure_read(83, 16)
    def checkPiTemp(self):
        # print("Run checkPiTemp!")
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            temp = float(f.read()) / 1000
            # print("Now temp is %.3f"%temp)
            if(temp > 47):
                self.openDev('F')
                self.fan_state = 1
            if(temp < 46):
                self.closeDev('F')
                self.fan_state = 0
        with open('./Data/data_base/pi_fan.csv', 'a') as f:
                f.write('%d %.3f %d\n'%(int(time.time()), temp, self.fan_state))
        Timer(30, self.checkPiTemp).start()
    def closeDev(self, device):
        self.secure_write(67, list((device+'\n').encode('ascii')), name = 'CLOSEDEV')

    def openDev(self, device):
        self.secure_write(79, list((device+'\n').encode('ascii')), name = 'OPENDEV')

    def nixieFormatString(self, string):
        n = string.count('.')
        l = len(string)
        ls = self.lastLEDString
        # ls = 'aaaaaaaa'
        if l == 8:
            while string.count('.'):
                p = string.find('.')
                ls = ls[:p]+ls[p].upper()+ls[p+1:]
                string = string[:p] + ' ' + string[p+1:]
            return string, ls
        elif l < 8:
            string = '%8s'%string
            while string.count('.'):
                p = string.find('.')
                ls = ls[:p]+ls[p].upper()+ls[p+1:]
                string = string[:p] + ' ' + string[p+1:]
            return string, ls
        elif l-n == 8:
            while string.count('.'):
                p = string.find('.')
                ls = ls[:p]+ls[p].upper()+ls[p+1:]
                string = string[:p] + string[p+1:]
            return string, ls
        elif l-n < 8:
            for _ in range(8-l+n):
                string = ' '+string
            while string.count('.'):
                p = string.find('.')
                ls = ls[:p]+ls[p].upper()+ls[p+1:]
                string = string[:p] + string[p+1:]
            return string, ls
        else:
            print('STRING ERR!')
            exit()
    def close(self):
        self.dev.close()


def randColor():
    a = np.random.randint(0,8,[8])
    l = ['r','g','b','a','y','p','w',' ']
    s = ''
    for i in a:
        s += l[i]
    return s



dev = Arduino(0x08)


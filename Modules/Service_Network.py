#!/usr/local/bin/python3
# -*- coding:utf-8 -*- 
'''
 * @Author: Aeonni 
 * @Date: 2018-10-05 09:05:25 
 * @Last Modified by:   Aeonni 
 * @Last Modified time: 2018-11-20 09:05:25 
 * @Blog: https://www.aeonni.com 
 * @Desc: 
'''
__version__ = '0.2.0'
moduleName = 'Network'

print('loading...Service_Network ver. ', __version__)

import os
import socket
import time
from threading import Timer
from multiprocessing import Value
from Modules.Aeonni_Nixie_Module import AN_Module

class Network(AN_Module):
    def __init__(self, dev):
        self.dev = dev
        AN_Module.__init__(self, moduleName, __version__)
        self.online = Value('i', 0)
        self.net_check()
        if(self.online.value):
            ip = self.get_host_ip()
            for each in ip.split('.'):
                self.dev.writeLED('gggggggg', self.moduleName)
                self.dev.writeNixie("%8s"%each, self.moduleName)
                print(each)
                time.sleep(1)
    def net_check(self):
        if os.system("ping -c 1 www.baidu.com"):
            self.online.value = 0
            return False
        self.online.value = 1
        return True
    def do_connect(self):
        os.system('netsh wlan connect name=Genius')
    def get_host_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        finally:
            s.close()
        return ip
    def put_state(self):
        if(self.online.value):
            ip = self.get_host_ip()
            # dev.
    # def run(self):
    #     if self.net_check():
    #         pass
    #     else:
    #         # self.do_connect()
    #         pass
    #     Timer(10, self.run()).start()

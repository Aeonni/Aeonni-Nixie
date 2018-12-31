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
moduleName = 'CLOCK'

print('loading...Service_Clock ver. ', __version__)

from threading import Thread, Event
from Modules.Aeonni_Nixie_Module import AN_Module
import time

class Clock(Thread, AN_Module):
    def __init__(self, dev):
        Thread.__init__(self)
        self.dev = dev
        AN_Module.__init__(self, moduleName, __version__)
        self.__running = Event()
        self.__running.set()
    def run(self):
        while True:
            self.dev.writeLED('        ', self.moduleName)
            self.dev.writeNixie(time.strftime("%Y.%m.%d"), self.moduleName)
            
            time.sleep(3)
            for _ in range(10):
                self.dev.writeNixie(time.strftime("%H.%M.%S"), self.moduleName)
                self.__running.wait() 
                time.sleep(0.8)
    def module_close(self):
        self.__running.clear()
        self.state = 'stopped'
    def module_open(self, opt = True):
        self.__running.set()
        self.state = 'running'
        return True
    # def getinfo(self):
    #     return dict(
    #         name = self.moduleName,
    #         ver = __version__,
    #         colors = dict(
    #             bg = '#fff',
    #             line = '#efae7c',
    #             logo = '#f9f1c0'
    #         ),
    #         state = 'running',
    #     )
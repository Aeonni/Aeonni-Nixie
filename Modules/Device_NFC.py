#!/usr/local/bin/python3
# -*- coding:utf-8 -*- 
'''
 * @Author: Aeonni 
 * @Date: 2018-10-10 09:05:22 
 * @Last Modified by:   Aeonni 
 * @Last Modified time: 2018-11-21 09:05:22 
 * @Blog: https://www.aeonni.com 
 * @Desc: 
'''

__version__ = '0.0.1'
moduleName = 'NFC'

print('loading...Device_NFC ver. ', __version__)

import os
import sys
lib_path = os.path.abspath('./Modules')
sys.path.append(lib_path)
from Modules.Aeonni_Nixie_Module import AN_Module

from py532lib.mifare import *
import threading
import random
import time


class NFC(AN_Module):
    def __init__(self, dev):
        self.dev = dev
        # self.moduleName = 'NFC'
        AN_Module.__init__(self, moduleName, __version__)
        self.state = 'stopped'
        self.card = Mifare()
        self.card.SAMconfigure()
        self.card.set_max_retries(MIFARE_SAFE_RETRIES)
        self.Sem = threading.Semaphore(1)
        self.cu_auth_id = -1
    def read_with_auth_a(self, addr, key=MIFARE_FACTORY_KEY):
        self.Sem.acquire()
        try:
            uid = self.card.scan_field()
            if uid:
                self.card.mifare_auth_a(addr, key)
                data = self.card.mifare_read(addr)
                self.card.in_deselect()
                # print('auth succ')
            else:
                data = None
                # print('no card')
        except:
            # print('auth err')
            uid = None
            data = None
        self.Sem.release()
        return dict(uid=uid, data=data)
    @AN_Module.isRunning
    def do_auth(self, addr, authf, auth_id, key=MIFARE_FACTORY_KEY):
        if auth_id == self.cu_auth_id:
            self.dev.openDev('P')
            self.dev.writeLED('yYyyyyyy', self.moduleName)
            self.dev.writeNixie('1.%.6d'%self.cu_auth_id, self.moduleName)
            r = self.read_with_auth_a(addr, key)
            if r['data'] is not None:
                return authf(r['data'])
        return False
    def reset_dev_prio(self):
        self.dev.resetPrio(self.moduleName)
    def generate_auth_id(self):
        self.cu_auth_id = random.randint(1,999999)
        self.cu_auth_id_gen_time = time.time()
        return self.cu_auth_id
    


    # def run(self):
    #     while True:
    #         self.dev.writeLED('        ', self.moduleName)
    #         self.dev.writeNixie(time.strftime("%Y.%m.%d"), self.moduleName)
            
    #         time.sleep(3)
    #         for _ in range(10):
    #             self.dev.writeNixie(time.strftime("%H.%M.%S"), self.moduleName)
    #             time.sleep(0.8)
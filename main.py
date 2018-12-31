#!/usr/local/bin/python3
# -*- coding:utf-8 -*- 
'''
 * @Author: Aeonni 
 * @Date: 2018-10-10 09:05:38 
 * @Last Modified by:   Aeonni 
 * @Last Modified time: 2018-10-10 09:05:38 
 * @Blog: https://www.aeonni.com 
 * @Desc: 
'''
__version__ = '0.1.0'

print('Starting...main ver. ', __version__)


import os
import sys
os.chdir('/home/pi/Aeonni-Nixie')

import threading
# import multiprocessing

from Modules.Device_I2CDev import dev
from Modules.Service_Clock import Clock
from Modules.Device_Cam import Cam
from Modules.Service_Figure import Fig
from Modules.Device_NFC import NFC
from Modules.Service_Network import Network

from Modules.Service_Module_Manager import ModuleManager

import AdminPanel.panel as panel

import Inori_onNixie.inori as inori

modules = dict()

if __name__ == '__main__':
    print('Initializing Modules...')
    cam = Cam('/home/pi/Aeonni-Nixie/Data/CamCapture/')
    fig = Fig('/home/pi/Aeonni-Nixie/Data/data_base/')
    nfc = NFC(dev)
    # net = Network(dev)
    clock = Clock(dev)

    print('Packing Modules to dict...')
    modules[cam.moduleName] = cam
    modules[fig.moduleName] = fig
    modules[nfc.moduleName] = nfc
    modules[clock.moduleName] = clock
    modules[dev.moduleName] = dev

    inori.device = modules[dev.moduleName]
    inori.cam = modules[cam.moduleName]
    inori.fig = modules[fig.moduleName]

    modules[inori.inori_ctrl.moduleName] = inori.inori_ctrl

    print('Adding Modules to Module_Manager...')
    module_manager = ModuleManager(modules)

    print('Starting Module Deamons...')
    modules['CLOCK'].start()
    modules[dev.moduleName].openDev('P')
    

    # threading.Thread(target=inori.start).start() # inori.start()

    panel.nfc_module = modules['NFC']
    panel.module_manager = module_manager
    panel.start()
    

    print('lalala')
    
    
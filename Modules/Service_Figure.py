#!/usr/local/bin/python3
# -*- coding:utf-8 -*- 
'''
 * @Author: Aeonni 
 * @Date: 2018-10-09 09:04:36 
 * @Last Modified by:   Aeonni 
 * @Last Modified time: 2018-10-10 09:04:36 
 * @Blog: https://www.aeonni.com 
 * @Desc: 
'''

__version__ = '0.1.1'
moduleName = 'FIGURE'

print('loading...Service_Figure ver. ', __version__)

import pandas as pd
import time
import matplotlib.pyplot as plt
from Modules.Aeonni_Nixie_Module import AN_Module

class Fig(AN_Module):
    def __init__(self, path):
        self.path = path
        AN_Module.__init__(self, moduleName, __version__)
    def genNewDHTFig(self):
        st = time.time()-60*60*24
        dht = pd.read_csv(self.path + "dht.csv", sep=' ', names=['time', 'temp', 'humi'], index_col=0)
        dht = dht[dht.index > st]
        dht.index = pd.to_datetime(dht.index.values, unit = 's', utc = True).tz_convert('Asia/Shanghai')
        dht.plot(secondary_y = ['humi'],figsize = [20,2])
        plt.savefig(self.path + 'dht.jpg', dpi=100)
    def genNewPiFig(self):
        st = time.time()-60*60*24
        pif = pd.read_csv(self.path + "pi_fan.csv", sep=' ', names=['time', 'temp', 'fan'], index_col=0)
        pif = pif[pif.index > st]
        pif.index = pd.to_datetime(pif.index.values, unit = 's', utc = True).tz_convert('Asia/Shanghai')
        m = pif['temp'].max() + 1
        M = pif['temp'].max() + 2
        pif['fan'][pif['fan'] == 0] = m
        pif['fan'][pif['fan'] == 1] = M
        pif.plot(figsize = [80,2])
        plt.savefig(self.path + 'pif.jpg', dpi=100)


if __name__ == '__main__':
    fig = Fig('/home/pi/Nixie/data_base/')
    fig.genNewFig()
#!/usr/local/bin/python3
# -*- coding:utf-8 -*- 
'''
 * @Author: Aeonni 
 * @Date: 2018-10-10 15:13:13 
 * @Last Modified by:   Aeonni 
 * @Last Modified time: 2018-10-10 15:13:13 
 * @Blog: https://www.aeonni.com 
 * @Desc: 
'''
import os

types = ['.py', '.c', '.h', '.ino', '.html', '.css']

path = './'

d = os.walk(path)

def readlines(fname):
    with open(fname, 'r') as f:
        r = f.readlines()
    return len(r)

totallines = 0

print(" NUMS : Filename")

for files in d:
    dname = files[0]
    if('py532lib' in dname or 'quick2wire' in dname ):
        continue
    for each in files[2]:
        for t in types:
            if each.endswith(t):
                fname = dname+'/'+each
                l = readlines(fname)
                totallines += l
                print("%4d  : "%l, fname)
                continue

print('Total Lines: %d'%totallines)
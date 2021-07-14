#!/usr/bin/python
import os
import sys
import serial
import math
import time
import datetime
from ..typings import UartOptions

# 删除RANGECMPB等超长字段
# RAWIMUSXB也可以删除
# inspvaxb可以设置为200、100、20hz试一下。
def configNovatel(ser):

    # need to change the following lever arm values when mounting in the car
    #'setimutoantoffset -0.2077 1.8782 1.0 0.10 0.10 0.10\r',\
    # 'setinstranslation ant2 x, y, z, std_x, std_y, std_z\r',\
    setupcommands7  = ['unlogall\r',\
                'serialconfig com1 230400 N 8 1 N OFF\r',\
                'ETHCONFIG ETHA AUTO AUTO AUTO AUTO\r',\
                'NTRIPCONFIG ncom1 client v1 58.215.20.43:2201 WX02 ymj_123 SIGEMZOOMQ1JDJI3\r',\
                'interfacemode ncom1 rtcmv3 novatel off\r',\
                'interfacemode com1 novatel novatel on\r',\
                'alignmentmode automatic\r',\
                'setinstranslation ant1 1.0 -0.37 -1.0 0.10 0.10 0.10\r',\
                'setinstranslation ant2 0.0 0.0 0.0 0.10 0.10 0.10\r',\
                'setinsrotation rbv -180 0 90\r',\
                #'setinsrotation rbv 90 0 180\r',\
                'setinstranslation user 1.0 -0.37 -1.0 0.10 0.10 0.10\r',\
                'log INSCONFIGB ONCHANGED\r',\
                'log RAWIMUSXB ONNEW\r',\
                'log versionb once\r',\
                'log rxconfigb once\r',\
                'log rxstatusb once\r',\
                'log thisantennatypeb once\r',\
                'log inspvaxb ontime 0.1\r',\
                #'log bestposb ontime 0.1\r',\
                'log bestgnssposb ontime 0.1\r',\
                #'log bestgnssvelb ontime 0.1\r',\
                #'log heading2b onnew\r',\
                'log ncom1 gpgga ontime 1\r',\
                'saveconfig\r']
        
    for cmd in setupcommands7:
        ser.write(cmd.encode())    

def start(options: UartOptions):
    port = options.path #need update
    ser = serial.Serial(port, options.baudrate, parity='N', bytesize = 8, 
                        stopbits = 1, timeout = None) #novatel

    if not os.path.exists('data/'):
        os.mkdir('data/')

    fname = './data/novatel-'
    ser.flushInput()
    fmode = 'wb'
    while True:
        if ser.isOpen(): break

    print ('\Port is open now\n')
    configNovatel(ser)
    ser.flushInput()

    fname += time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime()) + '.bin'

    with open(fname,fmode) as outf:
        while True:
            try:
                line = ser.readline()
                outf.write(bytes(line))  #line.decode('utf-8')

            except Exception as e:
                print(e)

# -*- coding: utf-8 -*-
"""
Created on Wed Jul 26 11:38:31 2017

@author: Athresh
"""

import win32api, win32con
import time
import win32gui
import win32ui
from scipy import misc
import glob
import numpy as np
from PIL import Image

global first_threshold,second_threshold,increase
first_threshold=18
second_threshold=54

def drag(x,y,x2,y2):
    win32api.SetCursorPos((x,y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
    time.sleep(0.1)
    win32api.SetCursorPos((x2,y2))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x2,y2,0,0)

def screenshot():
    global ScIter,imgGS
    #hwnd = win32gui.FindWindow(None, windowname)
    wDC = win32gui.GetWindowDC(hwnd)
    dcObj=win32ui.CreateDCFromHandle(wDC)
    cDC=dcObj.CreateCompatibleDC()
    dataBitMap = win32ui.CreateBitmap()
    dataBitMap.CreateCompatibleBitmap(dcObj, w, h)
    cDC.SelectObject(dataBitMap)
    cDC.BitBlt((0,0),(w, h) , dcObj, (700,200), win32con.SRCCOPY)
    
    #ScIter=ScIter+1
    bmpfilename = 'screenshot' + str(ScIter) + '.png'
    dataBitMap.SaveBitmapFile(cDC, bmpfilename)
    # Free Resources
    dcObj.DeleteDC()
    cDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, wDC)
    win32gui.DeleteObject(dataBitMap.GetHandle())
    
    
    imagepath = 'screenshot' + str(ScIter) +'.png'
    image = misc.imread(imagepath)
    img = Image.open(imagepath).convert('LA')
    GSImagePath = 'greyscale.png' + str(ScIter) +'.png'
    img.save(GSImagePath)
    imgGS = misc.imread(GSImagePath)
    for i in range(0,h):
        for j in range(0,w):
            if imgGS[i,j,0]<128:
                imgGS[i,j,0]=0 #black
            else:
                imgGS[i,j,0]=255 #white
                     
    bwfile = Image.fromarray(imgGS)
    resultBWPath = 'result_bw' + str(ScIter) + '.png'
    bwfile.save(resultBWPath)


def getCoord():
    global ScIter,ycoord
    flag1=0
    #bwimg = misc.imread("result_bw.png")
    horBar = 7
    verBar = 13
    
    #detect position of the basket
    for j in range(0,w-10):
        if flag1==1:
            break
        for i in range(0,h-2):
            if ((imgGS[i,j,0]==0 and imgGS[i+1,j,0]!=0)):
                ycoord=i
                flag2=0
                for k in range(1,horBar):
                    if(imgGS[ycoord+k,j,0]==0):
                        flag2=1
                        break
                
                if(flag2==0 and imgGS[ycoord+horBar+1,j,0]==0):
                    ycoord=ycoord+184
                    flag1=1
                    break
                
                
    if(ycoord>=580):
        return np.array([-1,-1])
           
    flag1=0
    for i in range(ycoord-50,ycoord):     
        if flag1==1:
            break
        for j in range(0,w-111):
            if ((imgGS[i,j,0]==0 and imgGS[i,j+1,0]!=0)):
                xcoord=j
                flag2=0
                for k in range(1,verBar):
                    if(imgGS[i,xcoord+k,0]==0):
                        flag2=1
                        break
                
                if(flag2==0 and imgGS[i,xcoord+verBar+1,0]==0):
                    xcoord=xcoord+62
                    flag1=1
                    break
                
    coords = np.empty(2,dtype='int')
    #mapping coordinates of the saved png and the actual screen
    coords[0]=xcoord+700
    coords[1]=ycoord+170
          
    imgGS[ycoord,xcoord,0]=100
    bwfile = Image.fromarray(imgGS)
    bwtestpath = 'result_bw_test' + str(ScIter) + '.png'
    bwfile.save(bwtestpath)
    return coords
    
    


def stage1():
    screenshot()
    coords=getCoord()
    
    #calculate x2
    if(coords[0]<startX):
        x2 = int(startX - (startY - 850)*(startX - coords[0])/(startY - coords[1]))
    elif(coords[0]>startX):
        x2 = int(startX + (startY - 850)*(coords[0] - startX)/(startY - coords[1]))
    
    else:
        x2 = startX
    drag(startX,startY,x2,850)
    
    

def stage2():
    global ScIter
    cnt=0
    screenshot()
    #ScIter=ScIter-1
    coords = getCoord()
    if(coords[0]==-1):
        return
    prevCoords = coords
    while(coords[0]>startX or prevCoords[0]>=coords[0]):
        screenshot()
        prevCoords = coords
        coords = getCoord()
        if(prevCoords[0]==coords[0] and prevCoords[1]==coords[1]):
            cnt=cnt+1
        if(prevCoords[0]==coords[0] and prevCoords[1]==coords[1] and cnt>2):
            break
        time.sleep(0.5)
    
    #compensate for right side motion
    if(coords[1]>lower_bound):
        lead=lower_lead
    elif(coords[1]<upper_bound):
        lead=upper_lead
    else:
        lead=mid_lead
    if(cnt<=2):
        coords[0]=coords[0] + lead
    if(coords[0]<startX):
        x2 = int(startX - (startY - 850)*(startX - coords[0])/(startY - coords[1]))
    elif(coords[0]>startX):
        x2 = int(startX + (startY - 850)*(coords[0] - startX)/(startY - coords[1]))
    
    else:
        x2 = startX
    drag(startX,startY,x2,850)
    



def main():
    time.sleep(2)
    global w,hwnd,h,startX,startY,ScIter,upper_bound,lower_bound,upper_lead,lower_lead,mid_lead
    upper_bound=520
    lower_bound=790
    upper_lead=165
    lower_lead=195
    mid_lead=180
    ScIter=0
    startX=950
    startY=900
    hwnd=0
    w=500
    h=580
    
    #known fixed position. ez
    for iter in range(0,6):
        stage1()
        time.sleep(4)
    
    for iter in range(0,70):
        stage2()
        time.sleep(4)
    
    
    
        

if __name__ == '__main__':
    main()
    
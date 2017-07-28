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
        for i in range(0,h-10):
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
                
    
    #If detection fails.          
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
    coords[0]=xcoord+702
    coords[1]=ycoord+205
    
    imgGS[ycoord,xcoord,0]=100
    bwfile = Image.fromarray(imgGS)
    bwtestpath = 'result_bw_test' + str(ScIter) + '.png'
    bwfile.save(bwtestpath)
    return coords
    
    
def getShootDirection(startX,startY,basketX,basketY):
    
    global finalY
    #tweak basketY to account for the trajectory
    basketY = basketY + (540-basketY)/3
    
    if(basketX<startX):
        x2 = int(startX - (startY - finalY)*(startX - basketX)/(startY -basketY))
    elif(basketX>startX):
        x2 = int(startX + (startY - finalY)*(basketX - startX)/(startY - basketY))
    
    else:
        x2 = startX
    
    finalCoords = np.empty(4,dtype='int')
    finalCoords[0] = startX
    finalCoords[1] = startY
    finalCoords[2] = x2
    finalCoords[3] = finalY
               
    return finalCoords

def stage1():
    screenshot()
    coords=getCoord()
    
    #calculate final mouse position
    finalCoords=getShootDirection(startX,startY,coords[0],coords[1])
    
    #drag the mouse in the determined direction
    drag(finalCoords[0],finalCoords[1],finalCoords[2],finalCoords[3])
    
    

def stage2():
    
    #Take screenshots at regular intervals and check if basket position is right to initiate a throw.
    global ScIter
    cnt=0
    screenshot()
    #ScIter=ScIter-1
    coords = getCoord()
    if(coords[0]==-1):
        return
    prevCoords = coords
    while(coords[0]>startX-50 or prevCoords[0]>=coords[0] or coords[0]<startX-100):
        screenshot()
        prevCoords = coords
        coords = getCoord()
        #Check if stage2 has been initiated while basket is stationary
        if(prevCoords[0]==coords[0] and prevCoords[1]==coords[1]):
            cnt=cnt+1
        if(prevCoords[0]==coords[0] and prevCoords[1]==coords[1] and cnt>2):
            break
        time.sleep(0.4)
    
    #compensate for right side motion
    #if(coords[1]>lower_bound):
     #   lead=lower_lead
    #elif(coords[1]<upper_bound):
     #   lead=upper_lead
    #else:
     #   lead=mid_lead
    lead=(540-coords[1])/5 + 167
    if(cnt<=2):
        coords[0]=coords[0] + lead
              
    
    #Calculate final mouse position.
    finalCoords = getShootDirection(startX,startY,coords[0],coords[1])
    drag(finalCoords[0],finalCoords[1],finalCoords[2],finalCoords[3])


def main():
    time.sleep(2)
    global w,hwnd,h,startX,startY,ScIter,upper_bound,lower_bound,upper_lead,lower_lead,mid_lead,finalY
    
    #Initialize constants
    Num_throws=250
    upper_bound=520
    lower_bound=790
    upper_lead=165
    lower_lead=195
    mid_lead=180
    finalY=800
    ScIter=0
    startX=950
    startY=900
    hwnd=0
    w=500
    h=580
    
    for iter in range(0,6):
        stage1()
        time.sleep(4)
    
    for iter in range(0,Num_throws):
        stage2()
        time.sleep(4)
    

if __name__ == '__main__':
    main()
    
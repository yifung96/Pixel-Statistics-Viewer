# -*- coding: utf-8 -*-
"""
Created on Tue Jul 20 09:35:59 2021

@author: YF
"""

import os
import time
import SFile_Functions_rev4 as func

##  Create Folder to store database and result
if not os.path.exists('DataFolder\\sfile_Data'):
    os.makedirs('DataFolder\\sfile_Data')
if not os.path.exists('ResultFolder\\sfile_Data'):
    os.makedirs('ResultFolder\\sfile_Data')

###################################  Change Setting here  ###########################################
# [1: Analyse Pix Stats at Fail Sweep || 2: Pix Stats Min Max Avg]
mode = 1
param = ['Squal','Squal2','Shutter','Pix_Sum','Pix_Min','Pix_Max','Filter']    
#####################################################################################################

##  INIT Main Program
t0 = time.time()
##  Access database folder
dataPath = 'DataFolder\\sfile_Data\\'
resPath = 'ResultFolder\\sfile_Data\\'
folDat = func.ExtFolder(dataPath)
##  File Handling
for test in folDat.testfile:
    print("\nProcessing: ",test)
    #   Data Cleaning, Collecting
    currFile = dataPath+test
    fileDat = func.ExtFile(currFile)
    #   Output file
    currTime = (time.strftime("%m:%d:%H:%M:%S",time.localtime())).replace(':','')
    resfilename = resPath+currTime+'_mode'+str(mode)+'_'+(fileDat.topParam['Product']+fileDat.topParam['Surface']).replace(" ","")+".xlsx"
    #print(resfilename)
    #   Data Sorting, Analysing
    func.ProcData(fileDat,param,mode,resfilename)
    
ElapsedTime = round(float(time.time()-t0),2)
print("Time elapsed: ", ElapsedTime,"s")

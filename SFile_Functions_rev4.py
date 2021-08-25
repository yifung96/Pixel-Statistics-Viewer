# -*- coding: utf-8 -*-
"""
Created on Tue Jul 20 09:56:45 2021

@author: YF
"""

import pandas as pd
import os
import re
import numpy as np
#import matplotlib.pyplot as plt

class ExtFolder(object):
    def __init__(self,Basepath):
        self.Basepath = Basepath
        self.totalfile = None
        self.ReadFolder(self.Basepath)
        self.display()
        
    def ReadFolder(self,Basepath):
        #Check the files in the data folder
        #Input: Folder path; Output: List of test files
        testfile = []
        with os.scandir(Basepath) as entries:
            for entry in entries:
                if entry.is_file():
                    testfile.append(entry.name)        

        self.totalfile = len(testfile)
        self.testfile = testfile
    
    def display(self):
        print("Total Files in Folder: ",self.totalfile)
        for file in self.testfile:
            print(file)
            
class ExtFile(object):
    def __init__(self,FolPath):
       self.FolPath = FolPath
       self.topParam, self.product, self.rep = self.TopParam(self.FolPath)
       self.productParam = self.ProductParam(self.product)
       Database_Dict = {'Z':[],'Boresight':[],'Velocity':[],'Acceleration':[],'Direction':[],'ProcData':[]}
       self.Database_Dict = Database_Dict
       self.extract(self.productParam,self.FolPath,self.rep)
       
       
    def TopParam(self,FolPath):
        keywords = ["# SurfaceName", "# Primary Sweep", "# Secondary Sweep", "# Product", "# Repetitions"]
        KeyData= []
        with open(FolPath,"rt") as file:
            for line in file:
                Delimiter = re.match("#----", line)
                if Delimiter:
                    break
                else:
                    for keyw in keywords:
                        if keyw in line:
                            KeyData.append(line) 
        #Extract Key data and form new line
        file.close()
        for b in range(len(KeyData)):
            KeyData[b] = str((re.findall(r'\[.*?\]', KeyData[b])))[3:-3]
        Data_Dict = {'Surface':KeyData[0],'PrimarySweep':KeyData[1],'SecondarySweep':KeyData[2],'Product':KeyData[3],'Repetitions':int(float(KeyData[4]))}
        for key,value in Data_Dict.items():
            print(key,':',value)
        product = (str([Data_Dict[key] for key in ['Product']]))[2:-2]
        rep = Data_Dict['Repetitions']
        return Data_Dict,product,rep
        
    def extract(self,productParam,FolPath,rep):
        Header_Data = True
        repCount = 0
        DataParam = ["# Z", "# Boresight", "# Velocity", "# Acceleration", "# Direction"]
        KeyData = []
        Temp_Dict = {'Z':[],'Boresight':[],'Velocity':[],'Acceleration':[],'Direction':[]}
        with open(FolPath,"rt") as file:
            for line in file:
                if Header_Data:
                    #Enter into new Sweep
                    Delimiter = re.match("#\|inches", line)
                    if Delimiter:
                        #Append Header Data in Dict
                        for c in range(len(KeyData)):
                            KeyData[c] = str((re.findall(r'\[.*?\]', KeyData[c])))[3:-3]
                        Temp_Dict['Z'] = (float(KeyData[0]))
                        Temp_Dict['Boresight'] = (float(KeyData[1]))
                        Temp_Dict['Velocity'] = (float(KeyData[2]))
                        Temp_Dict['Acceleration'] = (float(KeyData[3]))
                        Temp_Dict['Direction'] = (KeyData[4])
                                                      
                        #Setup to collect Data for the respective Sweep
                        Temp_Dict['ProcData'] = pd.Series([None]*rep)
                        repData = []
                        repCount = 0
                        KeyData = []
                        Header_Data = False
                    else:
                        #Collect Header Data of new Sweep
                        for dat in DataParam:
                            if dat in line:
                                KeyData.append(line)
                else:
                    DataLine = re.search(",.*,", line)
                    Delimiter = re.match("#-------", line)
                    if Delimiter:
                        #Collect all data in one rep
                        repData_df = self.processRaw(self.productParam,repData)
                        Temp_Dict['ProcData'][repCount] = repData_df
                        repData = []
                        repCount+=1
                        
                    if repCount == rep:
                        #Collect all repData in one Sweep
                        for param in Temp_Dict:
                            self.Database_Dict[param].append(Temp_Dict[param])
                        Header_Data = True
                    else:
                        if DataLine:
                            #Collecting every line of data in one rep
                            line_data = line.replace(',',' ')
                            line_data = line_data.replace(':',' ')
                            line_data = line_data.split()
                            #print(line_data)
                            repData.append(line_data)
                            
            if len(repData)>0:
                repData_df = self.processRaw(self.productParam,repData)
                Temp_Dict['ProcData'][repCount] = repData_df
                for param in Temp_Dict:
                    self.Database_Dict[param].append(Temp_Dict[param])
                         
        file.close()
            
    def processRaw(self,productParam,DataIn):
       
       DataIn = np.array(DataIn)
       DataOut = {}
       DataOut['inches'] = DataIn[:,0].astype(np.float)
       DataOut['ipss'] = DataIn[:,1].astype(np.float)
       DataOut['g_s'] = DataIn[:,2].astype(np.float)
       DataOut['Lcos'] = DataIn[:,3].astype(np.float)
       DataOut['Lsin'] = DataIn[:,4].astype(np.float)
       DataOut['mx'] = DataIn[:,5].astype(np.float)
       DataOut['my'] = DataIn[:,6].astype(np.float)
       DataOut['ex'] = DataIn[:,7].astype(np.float)
       DataOut['ey'] = DataIn[:,8].astype(np.float)
       DataOut['RawX'] = self.hex2int(DataIn[:,9], nbits=16, twos=True)
       DataOut['RawY'] = self.hex2int(DataIn[:,10], nbits=16, twos=True)
       DataOut['CumX'] = np.cumsum(DataOut['RawX'])
       DataOut['CumY'] = np.cumsum(DataOut['RawY'])
       DataOut['Wakeup'] = DataIn[:,11].astype(np.float)
       DataOut['Squal'] = self.hex2int(DataIn[:,productParam[0]], nbits=16, twos=False)
       DataOut['Squal2'] = self.hex2int(DataIn[:,productParam[1]], nbits=16, twos=False)
       DataOut['Pix_Sum'] = self.hex2int(DataIn[:,productParam[2]], nbits=16, twos=False)
       DataOut['Pix_Max'] = self.hex2int(DataIn[:,productParam[3]], nbits=16, twos=False)
       DataOut['Pix_Min'] = self.hex2int(DataIn[:,productParam[4]], nbits=16, twos=False)
       DataOut['FrameSkip'] = self.hex2int(DataIn[:,productParam[7]], nbits=16, twos=False)
       DataOut['Filter'] = self.hex2int(DataIn[:,productParam[8]], nbits=16, twos=False)
       for d in range(DataIn.shape[0]):
           DataIn[d,5] = str(DataIn[d,productParam[5]])+str(DataIn[d,productParam[6]])
       DataOut['Shutter'] =  self.hex2int(DataIn[:,5], nbits=16, twos=True)
       
       repData_df = pd.DataFrame(DataOut)
       return repData_df
       
    def hex2int(self, hexstr, nbits=8, twos=True):
        """
        Converts hex string to a signed integer
        """
        num = []
        for h in hexstr:
            try:
                num_elem = int(h, 16)
            except ValueError:
                num_elem = 999
            num.append(num_elem)
        num = np.array(num)
        if twos:
            neg = num >= 2**(nbits-1)
            num[neg] = num[neg] - 2**nbits
        return num 
    
    def ProductParam(self,product):
       #[Squal,Squal2,pix_sum,pix_max,pix_min,shut_hi,shut_lo,FrameSkip,Filter]
        if product == 'Orca4_USB':
            param = [14,22,15,16,17,18,19,21,12]
        elif product == 'DOLPHIN3':
            param = [14,22,15,16,17,18,19,21,12]
        elif product == 'DOLPHIN3_FPGA':
            param = [14,22,15,16,17,18,19,21,12]
        elif product == 'FGS_USB_8L':
            param = [14,22,15,16,17,18,19,21,12]
        else:
            print("Product not registered - Default Settings")
            param = [14,22,15,16,17,18,19,21,12]
        return param
    
class ProcData(object):
    def __init__(self,fileDat,param,mode,resfilename):
        self.fileDat = fileDat
        self.mode = mode
        self.resfile = resfilename
        self.param = param
        pri_sweep = self.fileDat.topParam['PrimarySweep'] 
        if self.mode == 1 and pri_sweep != 'None':
            Res_Dict = self.analyze(self.fileDat,param)
            self.Result = Res_Dict
            self.present1(self.Result,self.resfile,self.param)           
        elif self.mode == 2 and pri_sweep != 'None':
            Res_Dict = self.mode2_run(self.fileDat,self.param)
            self.Result = Res_Dict
            self.present2(self.Result,self.resfile)
        elif pri_sweep == 'None':
            Res_Dict = self.mode3_run(self.fileDat,self.param)
            self.Result = Res_Dict
            self.present3(self.Result,self.resfile,self.param)
            
    def analyze(self,fileDat,param):
        #   Identify fail sweep
        sweep = fileDat.topParam['PrimarySweep']
        sweep_range = fileDat.Database_Dict[sweep]
        fail_thresh = 0.5
        first_cmp = True
        for sw in range(len(sweep_range)):
            rep_sum = []
            for rep in range(5):
                repData = sum(fileDat.Database_Dict['ProcData'][sw][rep]['RawY'])
                rep_sum.append(repData)
            rep_average = self.average(rep_sum) 
            rep_min = min(rep_sum)
            if first_cmp:
                prev_average = rep_average
                first_cmp = False
            else:
                ind1 = (prev_average - rep_min)/prev_average
                #   Compare Current Minimum with Previous Average
                if ind1>fail_thresh:
                    break
                else:
                    prev_average = rep_average
        #   Identify fail rep
        r_cnt = 0
        r_fail = []
        for r in rep_sum:
            ind2 = (prev_average - r)/prev_average
            if ind2>fail_thresh:
                r_fail.append(r_cnt)
                r_cnt+=1
            else:
                r_cnt+=1
        print('Delta Loss Detected at ',sweep,': ',fileDat.Database_Dict['Velocity'][sw],'@Rep: ',r_fail)
        #   Identify the root cause from the fail rep
        repetition = fileDat.topParam['Repetitions']
        Res_Dict = {}
        for par in param:
            Res_Dict[par] = {}
            for reps in range(repetition):
                Res_Dict[par]["rep"+str(reps)] = fileDat.Database_Dict['ProcData'][sw][reps][par]
        return Res_Dict        
           
    def present1(self,Result,resfile,param):
        with pd.ExcelWriter(resfile, engine='xlsxwriter') as resBook:
            for par in param:
                resDF = pd.DataFrame(Result[par])
                resDF.drop(resDF.head(1).index, inplace=True)
                resDF.fillna('',inplace = True)
                resDF.to_excel(resBook, sheet_name = par)
                #Plot Result
                workbook = resBook.book
                worksheet = resBook.sheets[par]
                chart = workbook.add_chart({'type': 'scatter','subtype':'straight_with_markers'})
                max_row = resDF.shape[0]
                max_col = resDF.shape[1]+1
                for col in range(1,max_col):
                    chart.add_series({'name':[par,0,col],'categories':[par,1,1,max_row,0],
                                  'values':[par,1,col,max_row,col],'marker':{'type': 'circle', 'size': 2}})
                chart.set_x_axis({'name': 'Index'})
                chart.set_y_axis({'name': par,'major_gridlines': {'visible': False}})
                worksheet.insert_chart('E1', chart) 
  
            resBook.save()
            
    def average(self,oridata):
        dataave = round(sum(oridata)/len(oridata))
        return dataave
    
    #   Mode2 Function      
    def mode2_run(self,fileDat,param):
        
        Res_Dict = {}
        sw1 = fileDat.topParam['PrimarySweep']
        sw1_range = fileDat.Database_Dict[sw1]
        Res_Dict['Param'] = []
        Res_Dict['Param'].append(sw1)
        Res_Dict[sw1] = sw1_range
        #Get Min Max and Avg value from desired Param
        for par in param:
            Res_Dict['Param'].append(par)
            Res_Dict[par] = {}
            Res_Dict[par]['Max'] = []
            Res_Dict[par]['Min'] = []
            Res_Dict[par]['Avg'] = []
            for sw in range(len(sw1_range)):
                rep_max = []
                rep_min = []
                rep_avg = []
                for rep in range(5):
                    repData = fileDat.Database_Dict['ProcData'][sw][rep][par]
                    rep_max.append(max(repData))
                    tmp_avg = self.average(repData)
                    rep_avg.append(tmp_avg)
                    if tmp_avg > 0:
                        repData = np.array(repData)
                        rep_min.append(np.min(repData[np.nonzero(repData)]))
                    else:
                        rep_min.append(min(repData))
                        
                sw_max = max(rep_max)
                sw_min = min(rep_min)
                sw_avg = self.average(rep_avg)
                Res_Dict[par]['Max'].append(sw_max)
                Res_Dict[par]['Min'].append(sw_min)
                Res_Dict[par]['Avg'].append(sw_avg)
        return Res_Dict            
        
    def present2(self,Result,resfile):
        param = Result['Param']
        sweep = param[0]
        if sweep == 'Z':
            maj_unit = 0.1
            min_unit = 0.05
        else:
            maj_unit = 10
            min_unit = 5
        with pd.ExcelWriter(resfile, engine='xlsxwriter') as resBook:
            for item in range(1,len(param)):
                par_name = param[item]
                resDF = pd.DataFrame(Result[sweep],columns=[sweep])
                #Create DataFrame
                for par in Result[par_name]:
                    resDF[par] = Result[par_name][par]
                
                resDF.to_excel(resBook, sheet_name = par_name)
                workbook = resBook.book
                worksheet = resBook.sheets[par_name]
            
                #Plot Result
                chart = workbook.add_chart({'type': 'scatter','subtype':'straight_with_markers'})
                max_row = resDF.shape[0]
                max_col = resDF.shape[1]+1
                for col in range(2,max_col):
                    chart.add_series({'name':[par_name,0,col],'categories':[par_name,1,1,max_row,1],
                                  'values':[par_name,1,col,max_row,col],'marker':{'type': 'circle', 'size': 6}})
                chart.set_x_axis({'name': sweep,'major_unit':maj_unit,'minor_unit':min_unit}) #If Z major 0.1
                chart.set_y_axis({'name': par_name,'major_gridlines': {'visible': False}})
                worksheet.insert_chart('E1', chart) 
                
            resBook.save()        
  
    #   Mode 3 Function
    def mode3_run(self,fileDat,param):
        Res_Dict = {}
        rep = fileDat.topParam['Repetitions']
        for par in param:
            Res_Dict[par] = {}
            for rep in range(5):
                Res_Dict[par]["rep"+str(rep)] = fileDat.Database_Dict['ProcData'][0][rep][par]
                
        return Res_Dict
    
    def present3(self,Result,resfile,param):
        with pd.ExcelWriter(resfile, engine='xlsxwriter') as resBook:
            for par in param:
                resDF = pd.DataFrame(Result[par])
                resDF.drop(resDF.head(1).index, inplace=True)
                resDF.fillna('',inplace = True)
                resDF.to_excel(resBook, sheet_name = par)
                #Plot Result
                workbook = resBook.book
                worksheet = resBook.sheets[par]
                chart = workbook.add_chart({'type': 'scatter','subtype':'straight_with_markers'})
                max_row = resDF.shape[0]
                max_col = resDF.shape[1]+1
                for col in range(1,max_col):
                    chart.add_series({'name':[par,0,col],'categories':[par,1,1,max_row,0],
                                  'values':[par,1,col,max_row,col],'marker':{'type': 'circle', 'size': 2}})
                chart.set_x_axis({'name': 'Index'})
                chart.set_y_axis({'name': par,'major_gridlines': {'visible': False}})
                worksheet.insert_chart('E1', chart) 
  
            resBook.save()        
        
        
        
        
        
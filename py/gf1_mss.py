#coding=utf-8 
#! python
#-*- coding:utf-8 -*-
import os
import string
import ntpath
import glob
import re

def findAllFiles(infolder, pat = r'.txt$'):
    fileList = []
    for root, dirs, files in os.walk(infolder):
        for file in files:
            match = re.search(pat, file, re.I)
            if match:
                fileList.append(os.path.join(root, file))
    return fileList


inFolder = r'I:\golf\data'
outFolder = r'I:\result\gf1\mss-albers'
prjFile = r'G:\gf1_mss.txt'
prefFile = r'D:\opensource\ossim\preference.txt'
if not os.path.exists(outFolder):
    os.makedirs(outFolder)

#ZY02C_HRC_E116.3_N39.8_20141018_L1C0001878745-HR1.tiff
fileList = findAllFiles(inFolder, pat = r'GF1_PMS.*MSS[1-2]\.tiff$')
#fileList = findAllFiles(inFolder, pat = r'GF1_PMS.*MSS[1-2]\.tiff$')
#print mssFileList

nFiles = len(fileList)
i = 1

for i in range(0,nFiles):
    print('%d of %d:' %(i+1, nFiles))
    file = fileList[i]
    basename = os.path.basename(file)
    name_without_ext = os.path.splitext(basename)[0]
    print(name_without_ext)
    outFile = outFolder + '\\' + name_without_ext + '.tif'
    if os.path.isfile(outFile):
        continue
    #orthCmd = 'img-orth -i %s -prj %s -pref %s -o %s' %(file, prjFile, prefFile, outFile)
    orthCmd = 'gdalwarp -rpc -t_srs %s %s %s -multi' %(r'E:\albers.prf', file, outFile)
    os.system(orthCmd)

os.system('pause')

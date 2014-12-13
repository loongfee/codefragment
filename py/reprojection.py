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

###
inFolder = r'I:\result\zy02c\mss'
outFolder = r'I:\result\zy02c\mss-albers'
prjFile = r'E:\albers.prf'
if not os.path.exists(outFolder):
    os.makedirs(outFolder)

#ZY02C_HRC_E116.3_N39.8_20141018_L1C0001878745-HR1.tiff
fileList = findAllFiles(inFolder, pat = r'.*\.tif$')
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
    orthCmd = "gdalwarp -t_srs %s %s %s" %(prjFile, file, outFile)
    os.system(orthCmd)
    
######
inFolder = r'I:\result\zy02c\pan'
outFolder = r'I:\result\zy02c\pan-albers'
prjFile = r'E:\albers.prf'
if not os.path.exists(outFolder):
    os.makedirs(outFolder)
#ZY02C_HRC_E116.3_N39.8_20141018_L1C0001878745-HR1.tiff
fileList = findAllFiles(inFolder, pat = r'.*\.tif$')
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
    orthCmd = "gdalwarp -t_srs %s %s %s" %(prjFile, file, outFile)
    os.system(orthCmd)
    
######
inFolder = r'I:\result\gf1\mss'
outFolder = r'I:\result\gf1\mss-albers'
prjFile = r'E:\albers.prf'
if not os.path.exists(outFolder):
    os.makedirs(outFolder)
#ZY02C_HRC_E116.3_N39.8_20141018_L1C0001878745-HR1.tiff
fileList = findAllFiles(inFolder, pat = r'.*\.tif$')
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
    orthCmd = "gdalwarp -t_srs %s %s %s" %(prjFile, file, outFile)
    os.system(orthCmd)

######
inFolder = r'I:\result\gf1\pan'
outFolder = r'I:\result\gf1\pan-albers'
prjFile = r'E:\albers.prf'
if not os.path.exists(outFolder):
    os.makedirs(outFolder)
#ZY02C_HRC_E116.3_N39.8_20141018_L1C0001878745-HR1.tiff
fileList = findAllFiles(inFolder, pat = r'.*\.tif$')
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
    orthCmd = "gdalwarp -t_srs %s %s %s" %(prjFile, file, outFile)
    os.system(orthCmd)
os.system('pause')

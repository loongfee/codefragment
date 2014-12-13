#coding=utf-8 
#! python
#-*- coding:utf-8 -*-

import os
import sys
import string
from osgeo import gdal,ogr,osr
import ntpath
import glob
import re

inFolder = r'G:\l5-tm-120-031-20050906-l4-00001079'
outFolder = r'E:'


fileList = []

def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

pat = r'.tif$'
pat = r'.*_B1\.TIF$'
for root, dirs, files in os.walk(inFolder):
    for file in files:
      match = re.search(pat, file, re.I)
      if match:
        fileList.append(os.path.join(root, file))

nFiles = len(fileList)
i = 1    
for file in fileList:
    print('%d of %d:' %(i, nFiles))
    if outFolder == '':  
        new_extension = '.txt'
        (outBasename, ext) = os.path.splitext(file)
        outFile = outBasename + new_extension
    else:
        if not os.path.exists(outFolder):
            os.makedirs(outFolder)
        inDirName = os.path.dirname(file)
        inFilename = os.path.basename(file)
        (outBasename, ext) = os.path.splitext(inFilename)
        new_extension = '.txt'
        outFile = outFolder + '\\' + outBasename + new_extension
    print(outFile)
    cmd = 'boundary_date.py -i %s -o %s' %(file, outFile)
    os.system(cmd)
    i += 1
#coding=utf-8 
#! python
#-*- coding:utf-8 -*-

import ftplib
from ftplib import FTP
import os
import socket
import string
#from SOAPpy import SOAPProxy
#from suds.client import Client
#from pysimplesoap.client import SoapClient
import urllib
import urllib.request
#import urlparse
#from osgeo import gdal,ogr,osr
import ntpath
import glob
import re
import xml.etree.ElementTree
from time import gmtime, strftime
import progressbar

def findAllFiles(infolder, pat = r'.txt$'):
    fileList = []
    for root, dirs, files in os.walk(infolder):
        for file in files:
            match = re.search(pat, file, re.I)
            if match:
                fileList.append(os.path.join(root, file))
    return fileList

def iequal(a, b):
    try:
        return a.upper() == b.upper()
    except AttributeError:
        return a == b

listFile = 'filelist.txt'

class MYFTP:
    def __init__(self, hostaddr, username, password, remotedir, port=21):
        self.hostaddr = hostaddr
        self.username = username
        self.password = password
        self.remotedir  = remotedir
        self.port     = port
        self.ftp      = FTP(hostaddr)
        self.file_list = []
        # self.ftp.set_debuglevel(2)
    def __del__(self):
        self.ftp.close()
        # self.ftp.set_debuglevel(0)
    def login(self):
        ftp = self.ftp
        try: 
            timeout = 300
            socket.setdefaulttimeout(timeout)
            ftp.set_pasv(True)
            #print u'开始连接到 %s' %(self.hostaddr)
            #ftp.connect(self.hostaddr, self.port)
            print(u'成功连接到 %s' %(self.hostaddr))
            print(u'开始登录到 %s' %(self.hostaddr))
            ftp.login(self.username, self.password)
            print(u'成功登录到 %s' %(self.hostaddr))
            debug_print(ftp.getwelcome())
        except Exception:
            print(u'连接或登录失败')
        try:
            ftp.cwd(self.remotedir)
        except(Exception):
            print(u'切换目录失败')

    def is_same_size(self, localfile, remotefile):
        try:
            remotefile_size = self.ftp.size(remotefile)
        except:
            remotefile_size = -1
        try:
            localfile_size = os.path.getsize(localfile)
        except:
            localfile_size = -1
        debug_print('localfile_size:%d  remotefile_size:%d' %(localfile_size, remotefile_size),)
        if remotefile_size == localfile_size:
            return 1
        else:
            return 0

    def ftp_connect(self, path=''):
        if path == '':
            path = self.remotedir
        link = FTP(host = self.hostaddr, timeout = 5) #Keep low timeout
        link.login(passwd = self.password, user = self.username)
        debug_print("%s - Connected to FTP" % strftime("%d-%m-%Y %H.%M"))
        link.cwd(path)
        return link

    def fpt_download(self, localfile, remotefile):
        self.ftp = self.ftp_connect()
        if self.is_same_size(localfile, remotefile):
            debug_print(u'%s 文件大小相同，无需下载' %localfile)
            return
        else:
            debug_print(u'>>>>>>>>>>>>下载文件 %s ... ...' %localfile)
    
        downloaded = open(localfile, 'wb')
        file_size = self.ftp.size(remotefile)
        
        max_attempts = 5 #I dont want death loops.        
        while file_size != downloaded.tell():
            try:
                debug_print("%s while > try, run retrbinary\n" % strftime("%d-%m-%Y %H.%M"))
                if downloaded.tell() != 0:
                    self.ftp.retrbinary('RETR ' + remotefile, downloaded.write, downloaded.tell())
                else:
                    self.ftp.retrbinary('RETR ' + remotefile, downloaded.write)
            except Exception as myerror:
                if max_attempts != 0:
                    debug_print("%s while > except, something going wrong: %s\n \tfile lenght is: %i > %i\n" %
                        (strftime("%d-%m-%Y %H.%M"), myerror, file_size, downloaded.tell())
                    )
                    self.ftp = self.ftp_connect()
                    max_attempts -= 1
                else:
                    break
        debug_print("Done with file, attempt to download m5dsum")

    def download_file(self, localfile, remotefile):
        if self.is_same_size(localfile, remotefile):
            debug_print(u'%s 文件大小相同，无需下载' %localfile)
            return
        else:
            debug_print(u'>>>>>>>>>>>>下载文件 %s ... ...' %localfile)
        #return
        file_handler = open(localfile, 'wb')
        self.ftp.retrbinary(u'RETR %s'%(remotefile), file_handler.write)
        file_handler.close()

    def download_files(self, localdir='./', remotedir='./'):
        try:
            self.ftp.cwd(remotedir)
        except:
            debug_print(u'目录%s不存在，继续...' %remotedir)
            return
        if not os.path.isdir(localdir):
            os.makedirs(localdir)
        debug_print(u'切换至目录 %s' %self.ftp.pwd())
        self.file_list = []
        self.ftp.dir(self.get_file_list)
        remotenames = self.file_list
        #print(remotenames)
        #return
        for item in remotenames:
            filetype = item[0]
            filename = item[1]
            local = os.path.join(localdir, filename)
            if filetype == 'd':
                self.download_files(local, filename)
            elif filetype == '-':
                self.download_file(local, filename)
        self.ftp.cwd('..')
        debug_print(u'返回上层目录 %s' %self.ftp.pwd())
    def upload_file(self, localfile, remotefile):
        if not os.path.isfile(localfile):
            return
        if self.is_same_size(localfile, remotefile):
            debug_print(u'跳过[相等]: %s' %localfile)
            return
        file_handler = open(localfile, 'rb')
        self.ftp.storbinary('STOR %s' %remotefile, file_handler)
        file_handler.close()
        debug_print(u'已传送: %s' %localfile)
    def upload_files(self, localdir='./', remotedir = './'):
        if not os.path.isdir(localdir):
            return
        localnames = os.listdir(localdir)
        self.ftp.cwd(remotedir)
        for item in localnames:
            src = os.path.join(localdir, item)
            if os.path.isdir(src):
                try:
                    self.ftp.mkd(item)
                except:
                    debug_print(u'目录已存在 %s' %item)
                self.upload_files(src, item)
            else:
                self.upload_file(src, item)
        self.ftp.cwd('..')

    def get_file_list(self, line):
        ret_arr = []
        file_arr = self.get_filename(line)
        if file_arr[1] not in ['.', '..']:
            self.file_list.append(file_arr)
            
    def get_filename(self, line):
        pos = line.rfind(':')
        while(line[pos] != ' '):
            pos += 1
        while(line[pos] == ' '):
            pos += 1
        file_arr = [line[0], line[pos:]]
        return file_arr
def debug_print(s):
    print(s)

def filename_from_url(url):
    #return os.path.basename(urlparse.urlsplit(url)[2])
    return os.path.dirname(urllib.parse.urlsplit(url)[2])

def download_file(fileUrl, outPath='', outFilename=''):
    HOST = os.path.basename(urllib.parse.urlsplit(fileUrl)[1])
    DIRN = os.path.dirname(urllib.parse.urlsplit(fileUrl)[2])
    FILE = os.path.basename(urllib.parse.urlsplit(fileUrl)[2])
    if outFilename == '':
        outFilename = FILE    
    outFile = outPath + r'/' + outFilename  
    try:
        f = ftplib.FTP(HOST)
    except (socket.error, socket.gaierror):
        print('ERROR:cannot reach " %s"' % HOST)
        return
        #print '***Connected to host "%s"' % HOST
    try:
        f.login()
    except ftplib.error_perm:
        print('ERROR: cannot login anonymously')
        f.quit()
        return
    #print '*** Logged in as "anonymously"'
    try:
        f.cwd(DIRN)
    except ftplib.error_perm:
        print('ERRORL cannot CD to "%s"' % DIRN)
        f.quit()
        return
    #print '*** Changed to "%s" folder' % DIRN
    try:
        #传一个回调函数给retrbinary() 它在每接收一个二进制数据时都会被调用
        f.retrbinary('RETR %s' % outFilename, open(outFilename, 'wb').write)
    except ftplib.error_perm:
        print('ERROR: cannot read file "%s"' % outFilename)
        os.unlink(outFilename)
    else:
        print('*** Downloaded "%s" to %s' % (outFile, outPath))
    f.quit()

listFile = 'list.txt'

def modis_download(product='MOD05_L2',
                    collection='5',
                    startTime='2008-01-01 00:00:00',
                    endTime='2008-01-01 23:59:59',
                    #startTime='2008-01-01',
                    #endTime='2008-01-01',
                    north=40,
                    south=30,
                    west=-80,
                    east=-70,
                    coordsOrTiles='coords',
                    dayNightBoth='DNB',
                    outPath='',
                    download_all=True):
    url = 'http://modwebsrv.modaps.eosdis.nasa.gov/axis2/services/MODAPSservices'
    client = SoapClient(wsdl=url,trace=False)
    response = client.AddIntegers(a=1,b=2)
    result = response['AddResult']
    print(result)   
    #client = Client(url)
    #client = SOAPProxy(url);
    fileIdList = client.searchForFiles(product=product,collection=collection,startTime=startTime,endTime=endTime,north=north,south=south,west=west,east=east,coordsOrTiles=coordsOrTiles,dayNightBoth=dayNightBoth);
    
    fileIds = ','.join(fileIdList)
    #print fileIds
    fileUrlList = client.getFileUrls(fileIds=fileIds);
    nFiles = len(fileUrlList)
    if nFiles == 0:
        print('failed to fetch any file')
        return
  
    if not download_all:
        nFiles = 1
    logFile = open(listFile, 'wb')
    #for fileUrl in fileUrlList:
    #  logFile.write('%s\n' %fileUrl)
    #logFile.close()
    for iFile in range(0,nFiles):    
        logFile.write('%s\n' %fileUrlList[iFile])
    logFile.close()
    
    HOST = os.path.basename(urllib.parse.urlsplit(fileUrlList[0])[1])
    DIRN = os.path.dirname(urllib.parse.urlsplit(fileUrlList[0])[2])
    f = MYFTP(HOST, '', '', DIRN)
    f.login()

    i = 1
    for iFile in range(0,nFiles):
        #for fileUrl in fileUrlList:
        fileUrl = fileUrlList[iFile]
        print('%d of %d..' %(i, nFiles))
        file_name = fileUrl.split('/')[-1]
        HOST = os.path.basename(urllib.parse.urlsplit(fileUrl)[1])
        DIRN = os.path.dirname(urllib.parse.urlsplit(fileUrl)[2])
        FILE = os.path.basename(urllib.parse.urlsplit(fileUrl)[2])
        try:
            f.ftp.cwd(DIRN)
        except ftplib.error_perm:
            print('ERRORL cannot CD to "%s"' % DIRN)
            continue
        if outPath == '':
            outFile = FILE
        else:
            outFile = outPath + r'/' + FILE
        f.download_file(FILE, outFile)
        i += 1
        #download_file(fileUrl)
    
from osgeo import gdal,ogr,osr

def GetExtent(gt,cols,rows):
    ''' Return list of corner coordinates from a geotransform

        @type gt:   C{tuple/list}
        @param gt: geotransform
        @type cols:   C{int}
        @param cols: number of columns in the dataset
        @type rows:   C{int}
        @param rows: number of rows in the dataset
        @rtype:    C{[float,...,float]}
        @return:   coordinates of each corner
    '''
    ext=[]
    xarr=[0,cols]
    yarr=[0,rows]

    for px in xarr:
        for py in yarr:
            x=gt[0]+(px*gt[1])+(py*gt[2])
            y=gt[3]+(px*gt[4])+(py*gt[5])
            ext.append([x,y])
            #print x,y
        yarr.reverse()
    return ext

def ReprojectCoords(coords,src_srs,tgt_srs):
    ''' Reproject a list of x,y coordinates.

        @type geom:     C{tuple/list}
        @param geom:    List of [[x,y],...[x,y]] coordinates
        @type src_srs:  C{osr.SpatialReference}
        @param src_srs: OSR SpatialReference object
        @type tgt_srs:  C{osr.SpatialReference}
        @param tgt_srs: OSR SpatialReference object
        @rtype:         C{tuple/list}
        @return:        List of transformed [[x,y],...[x,y]] coordinates
    '''
    trans_coords=[]
    transform = osr.CoordinateTransformation( src_srs, tgt_srs)
    for x,y in coords:
        x,y,z = transform.TransformPoint(x,y)
        trans_coords.append([x,y])
    return trans_coords
    
def download_for_txt(txtFile, outFolder):    
    product='MOD05_L2'
    collection='51'
    startTime='2008-01-01 00:00:00'
    endTime='2008-01-01 23:59:59'
    north=40
    south=30
    west=-80
    east=-70
    coordsOrTiles='coords'
    dayNightBoth='DNB'
    dayNightBoth='D'
    outPath=''
    download_all=False
    year = 2000
    month = 1
    day = 1
    for line in open(txtFile):
        strList = line.split('=')
        if len(strList) != 2:
            continue
        sName = (strList[0]).strip(' \t\n\r')
        if sName == 'north':
            north = float(strList[1])
        elif sName == 'south':
            south = float(strList[1])
        elif sName == 'west':
            west = float(strList[1])
        elif sName == 'east':
            east = float(strList[1])
        elif sName == 'year':
            year = int(strList[1])
        elif sName == 'month':
            month = int(strList[1])
        elif sName == 'day':
            day = int(strList[1])
            
    #startTime = '%04d-%02d-%02d 00:00:00' %(year, month, day)
    #endTime = '%04d-%02d-%02d 23:59:59' %(year, month, day)
    startTime = '%04d-%02d-%02d' %(year, month, day)
    endTime = '%04d-%02d-%02d' %(year, month, day)
    # get file ids
# Get a list of file IDs for the specified product, collection, time period, and geographic coordinates:
# 
# http://lance-modis.eosdis.nasa.gov/axis2/services/MWSLance/searchForFiles?products=MOD04_L2&collection=1&startTime=2013-04-28&endTime=2013-04-28&north=40&south=30&east=-70&west=-80&coordsOrTiles=coords
# Get a list of FTP URLs for the specified file IDs
# 
# http://lance-modis.eosdis.nasa.gov/axis2/services/MWSLance/getFileUrls?fileIds=206688338,206688383,206701233,206700924
# Get an OpenSearch compatible format for the specified product, collection, time period, and geographic coordinates:
# 
# http://lance-modis.eosdis.nasa.gov/axis2/services/MWSLance/getOpenSearch?products=MOD04_L2&collection=1&start=2013-04-28&stop=2013-04-28&bbox=-80,30,-70,40 
    url = 'http://modwebsrv.modaps.eosdis.nasa.gov/axis2/services/MODAPSservices'
    #client = SoapClient(wsdl=url)
    #response = client.AddIntegers(a=1,b=2)
    #result = response['AddResult']
    #print(result)   
    #client = Client(url)
    #client = SOAPProxy(url);
    urlRequest = 'http://lance-modis.eosdis.nasa.gov/axis2/services/MWSLance/searchForFiles?'
    #urlRequest = 'http://modwebsrv.modaps.eosdis.nasa.gov/axis2/services/MODAPSservices/searchForFiles?'
    urlRequest = 'http://modwebsrv.modaps.eosdis.nasa.gov/axis2/services/MODAPSservices/searchForFiles?'
    urlRequest += 'products=%s'%(product)
    urlRequest += '&collection=%s'%(collection)
    urlRequest += '&startTime=%s'%(startTime)
    urlRequest += '&endTime=%s'%(endTime)
    urlRequest += '&north=%s'%(north)
    urlRequest += '&south=%s'%(south)
    urlRequest += '&east=%s'%(east)
    urlRequest += '&west=%s'%(west)
    urlRequest += '&coordsOrTiles=%s'%(coordsOrTiles)
    urlRequest += '&dayNightBoth=%s'%(dayNightBoth)
    req=urllib.request.Request(urlRequest)
    f = urllib.request.urlopen(req)
    root = xml.etree.ElementTree.fromstring(f.read().decode('utf-8'))
    fileIdList = []
    for returnTag in root.findall('return'):
        fileIdList.append(returnTag.text)

    if fileIdList[0] == "No results":
        print('failed to fetch any file')
        return
    fileIds = ','.join(fileIdList)
    #print fileIdList
    
    urlRequest = 'http://modwebsrv.modaps.eosdis.nasa.gov/axis2/services/MODAPSservices/getFileUrls?'
    urlRequest += 'fileIds=%s'%(fileIds)
    
    req=urllib.request.Request(urlRequest)
    f = urllib.request.urlopen(req)
    root = xml.etree.ElementTree.fromstring(f.read().decode('utf-8'))
    fileUrlList = []
    for returnTag in root.findall('return'):
        fileUrlList.append(returnTag.text)
        
    #fileUrlList = client.getFileUrls(fileIds=fileIds)
    nFiles = len(fileUrlList)
    if nFiles == 0:
        print('failed to fetch any file')
        return

    if not download_all:
        # find the nearest time
        iNeareast = 0
        minDistance = 100.0
        timeZone = (east + west) / 30.0
        landsatGreenwichMeanTime = 10.5 - timeZone
        for iFile in range(0,nFiles):
            fileUrl = fileUrlList[iFile]
            if fileUrl == '':
                continue
            FILE = os.path.basename(urllib.parse.urlsplit(fileUrl)[2])
            # MOD05_L2.A2008099.0250.005.2008100160229.hdf
            strGreenwichMeanTime = FILE.split('.')[2]   # e.g. 0250
            greenwichMeanTime = int(strGreenwichMeanTime[0:2]) + int(strGreenwichMeanTime[2:4]) / 60.0
            delta = abs(landsatGreenwichMeanTime - greenwichMeanTime)
            if  delta < minDistance:
                minDistance = delta
                iNeareast = iFile
        neareastFileUrl = fileUrlList[iNeareast]
        if neareastFileUrl == '':
            return
            
        logFile = open(listFile, 'a')
        logFile.write('%s\n' %neareastFileUrl)
        logFile.close()
        HOST = os.path.basename(urllib.parse.urlsplit(neareastFileUrl)[1])
        DIRN = os.path.dirname(urllib.parse.urlsplit(neareastFileUrl)[2])[1:]
        FILE = os.path.basename(urllib.parse.urlsplit(neareastFileUrl)[2])
        
        (outBasename1, ext) = os.path.splitext(FILE)
        (outBasename2, ext_old) = os.path.splitext(os.path.basename(txtFile))
        outFile = outFolder + '\\' + outBasename2 + '_' + outBasename1 + ext
        
#         myFtp = MYFTP(HOST, '', '', DIRN)
#         myFtp.fpt_download(outFile, FILE)
    

        ftp = FTP(HOST)
        ftp.login()
        ftp.cwd(DIRN)
         
        existingFileList = findAllFiles(outFolder, pat = outBasename2)
         
        for file in existingFileList:
            if not iequal(file, outFile):
                print('"%s" removed' %file)
                os.remove(file)
         
        # check the exist file
        remotefile_size = 0
        localfile_size = 0
        try:
            ftp.sendcmd("TYPE i")
            remotefile_size = ftp.size(FILE)
        except:
            remotefile_size = -1
        try:
            localfile_size = os.path.getsize(outFile)
        except:
            localfile_size = -1
        debug_print('localfile_size:%d  remotefile_size:%d' %(localfile_size, remotefile_size),)
        if remotefile_size == localfile_size:
            return
        else:
            #print outFile
            print('######  downloading:%s  ######' %(FILE))            
            filesize = ftp.size(FILE)
            progress = progressbar.AnimatedProgressBar(end=filesize, width=50)
            with open(outFile, 'wb') as f:
                def callback(chunk):
                    f.write(chunk)
                    progress + len(chunk)
                    # Visual feedback of the progress!
                    progress.show_progress()
                ftp.retrbinary('RETR %s'%FILE, callback)
            
#             with open(outFile, 'wb') as f:
#                 ftp.retrbinary('RETR %s' %FILE, f.write)
            #download_file(FILE, outFile)
            ftp.close()
            debug_print('')
    else:    
        ##HOST = os.path.basename(urlparse.urlsplit(fileUrlList[0])[1])
        ##DIRN = os.path.dirname(urlparse.urlsplit(fileUrlList[0])[2])
        i = 1
        for iFile in range(0,nFiles):
            #for fileUrl in fileUrlList:
            fileUrl = fileUrlList[iFile]
            if  fileUrl == '':
                continue
            #print '%d of %d..' %(i, nFiles)
            file_name = fileUrl.split('/')[-1]
            HOST = os.path.basename(urllib.parse.urlsplit(fileUrl)[1])
            DIRN = os.path.dirname(urllib.parse.urlsplit(fileUrl)[2])[1:]
            FILE = os.path.basename(urllib.parse.urlsplit(fileUrl)[2])
            #print fileUrl
            ftp = FTP(HOST)
            ftp.login()
            ftp.cwd(DIRN)
            #ftp = MYFTP(HOST, '', '', DIRN)
            #print HOST
            #ftp.login()
            #ftp.ftp.connect(HOST)
            #ftp.ftp.login()
            #ftp.ftp.cwd(DIRN)
            #try:
            #    print DIRN
            #    ftp.ftp.cwd(DIRN)
            #except ftplib.error_perm:
            #    print 'ERRORL cannot CD to "%s"' % DIRN
            #    continue
              
            (outBasename1, ext) = os.path.splitext(FILE)
            (outBasename2, ext_old) = os.path.splitext(os.path.basename(txtFile))
            outFile = outFolder + '\\' + outBasename2 + '_' + outBasename1 + ext
            
            # check the exist file
            remotefile_size = 0
            localfile_size = 0
            try:
                ftp.sendcmd("TYPE i")   # read by binary
                remotefile_size = ftp.size(FILE)
            except:
                remotefile_size = -1
            try:
                localfile_size = os.path.getsize(outFile)
            except:
                localfile_size = -1
            debug_print('localfile_size:%d  remotefile_size:%d' %(localfile_size, remotefile_size),)
            if remotefile_size == localfile_size:
                continue
            else:
                #print outFile
                print('######  downloading:%s  ######' %(FILE))
                with open(outFile, 'wb') as f:
                    ftp.retrbinary('RETR %s' %FILE, f.write)
                #ftp.download_file(FILE, outFile)
                ftp.close()
            i += 1

if __name__ == "__main__":
    f = open(listFile, 'w+')
    f.close()
    
    infolder = r'E:\landsat8\2014txt'
    #infolder = r'E:\landsat8\1'
    outfolder = r'G:\l8_modis\2010'
    
    infolder = r'E:\landsat8\2000\txt'
    outfolder = r'G:\l8_modis\2000'

    infolder = r'E:\landsat8\2014_cenAsiantxt'
    outfolder = r'G:\modis\cenAsian2014'

    fileList = []

    pat = r'.txt$'
    for root, dirs, files in os.walk(infolder):
        for file in files:
            match = re.search(pat, file, re.I)
            if match:
                fileList.append(os.path.join(root, file))

    if not os.path.exists(outfolder):
        os.makedirs(outfolder)
    nFiles = len(fileList)
    #i = 47
    for i in range(0,nFiles):
    #for file in fileList:
        print('%d of %d:' %(i+1, nFiles))
        download_for_txt(fileList[i], outfolder)
        #i += 1
    os.system('pause')

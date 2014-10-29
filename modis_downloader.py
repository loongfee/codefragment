#coding=utf-8 
#! python
#-*- coding:utf-8 -*-

import ftplib
from ftplib import FTP
import os
import socket
import string
from SOAPpy import SOAPProxy
import urlparse
from osgeo import gdal,ogr,osr

listFile = 'filelist.txt'

class MYFTP:
    def __init__(self, hostaddr, username, password, remotedir, port=21):
        self.hostaddr = hostaddr
        self.username = username
        self.password = password
        self.remotedir  = remotedir
        self.port     = port
        self.ftp      = FTP()
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
            print u'开始连接到 %s' %(self.hostaddr)
            ftp.connect(self.hostaddr, self.port)
            print u'成功连接到 %s' %(self.hostaddr)
            print u'开始登录到 %s' %(self.hostaddr)
            ftp.login(self.username, self.password)
            print u'成功登录到 %s' %(self.hostaddr)
            debug_print(ftp.getwelcome())
        except Exception:
            print u'连接或登录失败'
        try:
            ftp.cwd(self.remotedir)
        except(Exception):
            print u'切换目录失败'

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
    print s

def filename_from_url(url):
    #return os.path.basename(urlparse.urlsplit(url)[2])
    return os.path.dirname(urlparse.urlsplit(url)[2])

def download_file(fileUrl, outPath='', outFilename=''):
  HOST = os.path.basename(urlparse.urlsplit(fileUrl)[1])
  DIRN = os.path.dirname(urlparse.urlsplit(fileUrl)[2])
  FILE = os.path.basename(urlparse.urlsplit(fileUrl)[2])
  if outFilename == '':
    outFilename = FILE
    
  outFile = outPath + r'/' + outFilename
  
  try:
    f = ftplib.FTP(HOST)
  except (socket.error, socket.gaierror):
    print 'ERROR:cannot reach " %s"' % HOST
    return
  #print '***Connected to host "%s"' % HOST

  try:
    f.login()
  except ftplib.error_perm:
    print 'ERROR: cannot login anonymously'
    f.quit()
    return
  #print '*** Logged in as "anonymously"'
  try:
    f.cwd(DIRN)
  except ftplib.error_perm:
    print 'ERRORL cannot CD to "%s"' % DIRN
    f.quit()
    return
  #print '*** Changed to "%s" folder' % DIRN
  try:
    #传一个回调函数给retrbinary() 它在每接收一个二进制数据时都会被调用
    f.retrbinary('RETR %s' % outFilename, open(outFilename, 'wb').write)
  except ftplib.error_perm:
    print 'ERROR: cannot read file "%s"' % outFilename
    os.unlink(outFilename)
  else:
    print '*** Downloaded "%s" to %s' % (outFile, outPath)
  f.quit()


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
  url = 'http://modwebsrv.modaps.eosdis.nasa.gov/axis2/services/MODAPSservices';
  client = SOAPProxy(url);
  fileIdList = client.searchForFiles(product=product,collection=collection,startTime=startTime,endTime=endTime,north=north,south=south,west=west,east=east,coordsOrTiles=coordsOrTiles,dayNightBoth=dayNightBoth);

  fileIds = string.join(fileIdList, sep=',')
  #print fileIds
  fileUrlList = client.getFileUrls(fileIds=fileIds);
  nFiles = len(fileUrlList)
  if nFiles == 0:
    print 'failed to fetch any file'
    exit()
  
  if not download_all:
    nFiles = 1
    
  logFile = open(listFile, 'wb')
  #for fileUrl in fileUrlList:
  #  logFile.write('%s\n' %fileUrl)
  #logFile.close()
  for iFile in range(0,nFiles):    
    logFile.write('%s\n' %fileUrlList[iFile])
  logFile.close()
    
  HOST = os.path.basename(urlparse.urlsplit(fileUrlList[0])[1])
  DIRN = os.path.dirname(urlparse.urlsplit(fileUrlList[0])[2])
  f = MYFTP(HOST, '', '', DIRN)
  f.login()

  i = 1
  for iFile in range(0,nFiles):
  #for fileUrl in fileUrlList:
    fileUrl = fileUrlList[iFile]
    print '%d of %d..' %(i, nFiles)
    file_name = fileUrl.split('/')[-1]
    HOST = os.path.basename(urlparse.urlsplit(fileUrl)[1])
    DIRN = os.path.dirname(urlparse.urlsplit(fileUrl)[2])
    FILE = os.path.basename(urlparse.urlsplit(fileUrl)[2])
    try:
      f.ftp.cwd(DIRN)
    except ftplib.error_perm:
      print 'ERRORL cannot CD to "%s"' % DIRN
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
    
def download_for_tm(imageFile):
  ds=gdal.Open(imageFile)

  gt=ds.GetGeoTransform()
  cols = ds.RasterXSize
  rows = ds.RasterYSize
  ext=GetExtent(gt,cols,rows)

  src_srs=osr.SpatialReference()
  src_srs.ImportFromWkt(ds.GetProjection())
  #tgt_srs=osr.SpatialReference()
  #tgt_srs.ImportFromEPSG(4326)
  tgt_srs = src_srs.CloneGeogCS()

  geo_ext=ReprojectCoords(ext,src_srs,tgt_srs)
  #print type(geo_ext[0])
  #print geo_ext
  maxLonLat =  max(geo_ext)
  minLonLat =  min(geo_ext)
  
  basename = os.path.basename(imageFile)
  
  
  year = 2008
  month = 1
  day = 1
  north=40
  south=30
  west=-80
  east=-70
  
  #north = maxLonLat[1]
  #south = minLonLat[1]
  #west = minLonLat[0]
  #east = maxLonLat[0]
  #date = basename.split('-')[4]
  #year = int(date[0:4])
  #month = int(date[4:6])
  #day = int(date[6:8])
  
  #print '%d-%d-%d' %(year, month, day)
  outPath=os.path.dirname(imageFile)
  startTime = '%04d-%02d-%02d 00:00:00' %(year, month, day)
  endTime = '%04d-%02d-%02d 23:59:59' %(year, month, day)
  modis_download(startTime=startTime, endTime=endTime, north=north, south=south, west=west, east=east, outPath=outPath, dayNightBoth='D', download_all=False)
  #os.remove(listFile)

if __name__ == "__main__":
  download_for_tm(r'G:\l5-tm-120-031-20050906-l4-00001079\l5-tm-120-031-20050906-l4-00001079.tif')
  os.system('pause')
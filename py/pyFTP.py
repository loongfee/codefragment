#coding=utf-8 
#! python
#-*- coding:utf-8 -*-

import ftplib
from ftplib import FTP
import os
import socket
import string
import urllib.parse
import re
import warnings

listFile = 'filelist.txt'

class MYFTP:
    """
    Class adding recursive nlst() behavior to ftplib.FTP instance. The
    ftplib.FTP instance is available through the connection attribute, and
    is exposed through __getattr__.

    The behavior added by this class (recursive directory listing) is most
    appropriate for ftp connections on a local network over a fast connection, 
    or for small directories on remote ftp servers.

    The class relies on an externally defined callable, which can parse the
    lines returned by the ftplib.FTP.dir() method. This callable should be 
    bound to the 'dirparser' attribute on this object. The callable 'dirparser' 
    attribute can be initialized by passing it in to the constructor using the
    keyword argument 'dirparser', or by attaching the callable to the
    'dirparser' attribute after instantiation. 

    The callable should return parsed results as a dict. This class makes some
    assumptions about the contents of the dict returned by the user-defined 
    dirparser callable:

    -- the key 'trycwds' holds a list of booleans 

    -- the key 'names' holds a list of filenames in the dir() listing.
    
    -- The two lists should be the same length. A True value in the list
       referred to by the 'trycwds' key indicates the corresponding value
       in the list referred to by the 'names' key is a directory.

    -- The key names are based on fields in the ftpparse structure, from the   
       ftpparse module/C library.     
   
    -- Other keys can be included in the dict, but they are not used by the 
       rnlst() method.
      
    -- The callable should return an empty dict() if there is nothing to return
       from the dir listing.
       
    This module provides two parsers which seem to work ok, but it should
    be easy to create others if these don't work for some reason:

    -- parse_windows parses the dir listing from Windows ftp servers.
    -- parse_unix parses the dir listing from UNIX ftp servers.
    
    """
    def __init__(self, hostaddr, username, password, acct, dirparser=None, port=21):
        self.hostaddr = hostaddr
        self.username = username
        self.password = password
        self.port     = port
        self.connection = ftplib.FTP(hostaddr, username, password, acct)
        self.remotepathsep = '/'
        self.dirparser = dirparser
        self.file_list = []
        # self.ftp.set_debuglevel(2
        
    def __getattr__(self, name):
        """
        Delegate most requests to the underlying FTP object. 
        """
        
        return getattr(self.connection, name)


    def _dir(self,path):
        """
        Call dir() on path, and use callback to accumulate
        returned lines. Return list of lines.
        """

        dirlist = []
        try:
            self.connection.dir(path, dirlist.append)
        except ftplib.error_perm:
            warnings.warn('Access denied for path %s'%path)
        return dirlist


    def parsedir(self, path=''):
        """
        Method to parse the lines returned by the ftplib.FTP.dir(),
        when called on supplied path. Uses callable dirparser
        attribute. 
        """
        
        if self.dirparser is None:
            msg = ('Must set dirparser attribute to a callable '
                   'before calling this method')
            raise TypeError(msg)

        dirlines = self._dir(path)
        dirdict = self.dirparser(dirlines)
        return dirdict
        
        
    def _cleanpath(self, path):
        """
        Clean up path - remove repeated and trailing separators. 
        """
        
        slashes = self.remotepathsep*2
        while slashes in path:
            path = path.replace(slashes,self.remotepathsep)
            
        if path.endswith(self.remotepathsep):
            path = path[:-1]
            
        return path
        
        
    def _rnlst(self, path, filelist):
        """
        Recursively accumulate filelist starting at
        path, on the server accessed through this object's
        ftp connection.
        """
        
        path = self._cleanpath(path)
        dirdict = self.parsedir(path)
        
        trycwds = dirdict.get('trycwds', [])
        names = dirdict.get('names', [])
        
        for trycwd, name in zip(trycwds, names):
            fn = name.split('/')[-1]
            if name in ('.', '..'):
                continue
            if trycwd: # name is a directory
                self._rnlst(self.remotepathsep.join([path, name]), filelist)
            else: 
                filelist.append(self.remotepathsep.join([path, name]))
                
        return filelist

                
    def rnlst(self, path=''):
        """
        Recursive nlst(). Return a list of filenames under path.
        """
      
        filelist = []
        return self._rnlst(path,filelist)
    
    def traverse(self, filelist, depth=0):
        """
        return a recursive listing of an ftp server contents (starting
        from the current directory)
        
        listing is returned as a recursive dictionary, where each key
        contains a contents of the subdirectory or None if it corresponds
        to a file.
        
        @param ftp: ftplib.FTP object
        """
        if depth > 10:
            return ['depth > 10']
        level = {}
        for entry in (path for path in self.connection.nlst() if path not in ('.', '..')):
            try:
                self.connection.cwd(entry)
                level[entry] = self.traverse(filelist, depth+1)
                self.connection.cwd('..')
            except ftplib.error_perm:
                level[entry] = None
        return level
            
    def login(self):
        ftp = self.connection
        try: 
            timeout = 300
            socket.setdefaulttimeout(timeout)
            ftp.set_pasv(True)
            print(u'开始连接到 %s' %(self.hostaddr))
            ftp.connect(self.hostaddr, self.port)
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
            remotefile_size = self.connection.size(remotefile)
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
        self.connection.retrbinary(u'RETR %s'%(remotefile), file_handler.write)
        file_handler.close()

    def download_files(self, localdir='./', remotedir='./'):
        try:
            remotedir = self._cleanpath(remotedir)
            self.connection.cwd(remotedir)
        except:
            debug_print(u'目录%s不存在，继续...' %remotedir)
            return
        if not os.path.isdir(localdir):
            os.makedirs(localdir)
        debug_print(u'切换至目录 %s' %self.connection.pwd())
        
        
        dirdict = self.parsedir()
        
        trycwds = dirdict.get('trycwds', [])
        names = dirdict.get('names', [])
        nFiles = len(trycwds)
        for i in range(0, nFiles):
            filetype = trycwds[i]
            filename = names[i]
            if filename in ('.', '..'):
                continue
            local = os.path.join(localdir, filename)
            if filetype == 'd':
                self.download_files(local, filename)
                print(filename)
                return
            #elif filetype == '-':
            else:
                self.download_file(local, filename)
        
#         self.file_list = []
#         self.connection.dir(self.get_file_list)
#         #self.connection._dir(self.file_list.append)
#         remotenames = self.file_list
#         #print(remotenames)
#         #return
#         for item in remotenames:
#             filetype = item[0]
#             filename = item[1]
#             local = os.path.join(localdir, filename)
#             if filetype == 'd':
#                 self.download_files(local, filename)
#                 print(filename)
#                 return
#             elif filetype == '-':
#                 self.download_file(local, filename)
        #self.connection.cwd('..')
        #debug_print(u'返回上层目录 %s' %self.connection.pwd())
    def upload_file(self, localfile, remotefile):
        if not os.path.isfile(localfile):
            return
        if self.is_same_size(localfile, remotefile):
            debug_print(u'跳过[相等]: %s' %localfile)
            return
        file_handler = open(localfile, 'rb')
        self.connection.storbinary('STOR %s' %remotefile, file_handler)
        file_handler.close()
        debug_print(u'已传送: %s' %localfile)
    def upload_files(self, localdir='./', remotedir = './'):
        if not os.path.isdir(localdir):
            return
        localnames = os.listdir(localdir)
        self.connection.cwd(remotedir)
        for item in localnames:
            src = os.path.join(localdir, item)
            if os.path.isdir(src):
                try:
                    self.connection.mkd(item)
                except:
                    debug_print(u'目录已存在 %s' %item)
                self.upload_files(src, item)
            else:
                self.upload_file(src, item)
        self.connection.cwd('..')

    def get_file_list(self, line):
        ret_arr = []
        file_arr = self.get_filename(line)
        if file_arr[1] not in ['.', '..']:
            self.file_list.append(file_arr)
            
    def get_filename(self, line):
#         pos = line.rfind(':')
#         while(line[pos] != ' '):
#             pos += 1
#         while(line[pos] == ' '):
#             pos += 1
#         file_arr = [line[0], line[pos:]]
#         return file_arr            
        pattern = re.compile('(.)(.*?)\s+(.*?)\s+(.*?)\s+(.*?)\s+'
                             '(.*?)\s+(.*?\s+.*?\s+.*?)\s+(.*)')
        
        fields = 'trycwds tryretrs inodes users groups sizes dates names'.split()
        
        getmatches = lambda s:pattern.search(s)
        matches = filter(getmatches, line)
        getfields = lambda s:pattern.findall(s)[0]
        lists = list(zip(*map(getfields, matches)))
        file_arr = [lists[0], lists[-1]]
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
        
def listFiles(files, patern='^SJLC_.+.tar.gz'):
    matchedFiles = []
 
    for filename in files:
        if re.match(patern, filename):
            matchedFiles.append(filename)
    return matchedFiles


        

# Naive ftplib.FTP.dir() parsing functions, which may or may not work. (These
# happen to work for servers I connect to.) Create your own functions (perhaps
# using ftpparse) for more robust solutions.
       
def parse_windows(dirlines):
    """
    Parse the lines returned by ftplib.FTP.dir(), when called
    on a Windows ftp server. May not work for all servers, but it
    works for the ones I need to connect to.
    """

    typemap = {'<DIR>': True}
    
    if not dirlines:
        return dict()
    
    maxlen = max(len(line) for line in dirlines)
    columns = [slice(0, 9), slice(9, 17), slice(17, 29), slice(29, 38), 
               slice(38, maxlen+1)]

    fields = 'dates times trycwds sizes names'.split()

    values = []
    for line in dirlines:
        vals = [line[slc].strip() for slc in columns]
        vals[2] = typemap.get(vals[2], False)
        values.append(vals)
        
    lists = zip(*values)
    assert len(lists) == len(fields)

    return dict(zip(fields, lists))


def parse_unix(dirlines,startindex=0):
    """
    Parse the lines returned by ftplib.FTP.dir(), when called
    on a UNIX ftp server. May not work for all servers, but it
    works for the ones I need to connect to.
    """

    dirlines = dirlines[startindex:]
    if not dirlines:
        return dict()
   
    pattern = re.compile('(.)(.*?)\s+(.*?)\s+(.*?)\s+(.*?)\s+'
                         '(.*?)\s+(.*?\s+.*?\s+.*?)\s+(.*)')

    fields = 'trycwds tryretrs inodes users groups sizes dates names'.split()

    getmatches = lambda s:pattern.search(s)
    matches = filter(getmatches, dirlines)

    getfields = lambda s:pattern.findall(s)[0]
    lists = list(zip(*map(getfields, matches)))
    
    # change the '-','d','l' values to booleans, where names referring
    # to directories get True, and others get False.
    lists[0] = ['d' == s for s in lists[0]]
    
    assert len(lists) == len(fields)
    
    return dict(list(zip(fields, lists)))

def listFiles(files, patern='^SJLC_.+.tar.gz'):
    matchedFiles = []
 
    for filename in files:
        if re.match(patern, filename):
            matchedFiles.append(filename)
    return matchedFiles
            
def test():
    hostaddr = 'ftp://10.6.8.80/DOWNLOAD/LANDSAT-8'
    hostaddr = '10.6.8.80'
    username = 'sjg_user'
    password = 'x7Y#jPkbF9'
    remotedir = 'DOWNLOAD/LANDSAT-8'
    #hostaddr = '10.6.11.10'
    #username = 'jiaoweili'
    #password = 'jiaoweili'
    #remotedir = 'socketrow'
    f = MYFTP(hostaddr, username, password, '', dirparser=parse_unix)
    filelist = f.rnlst(path=remotedir)
#     filelist = []
#     filelist = f.traverse(filelist, 0)
    #f.connection.dir(filelist.append)
    mtlFilelist = listFiles(filelist, patern='.*MTL\.txt$')
    nTotal = len(mtlFilelist)
    counter = 1
    f_handle = open('list.txt', 'w+')
    for mtlFile in mtlFilelist:
        print('%s of %s..'%(counter, nTotal))
        try:
            #print(mtlFile, file=f_handle)            
            #mtlFile = line.strip()
            fileUrl = 'ftp://'+hostaddr+'/'+mtlFile
            HOST = os.path.basename(urllib.parse.urlsplit(fileUrl)[1])
            DIRN = os.path.dirname(urllib.parse.urlsplit(fileUrl)[2])
            FILE = os.path.basename(urllib.parse.urlsplit(fileUrl)[2])
            f.download_file('C:\\software\\mtl\\'+FILE, mtlFile)
            counter += 1
        except Exception as e:
            print(e)
            counter += 1
    f_handle.close()
            
def test1():
    hostaddr = '10.6.8.80'
    username = 'sjg_user'
    password = 'x7Y#jPkbF9'
    remotedir = 'DOWNLOAD/LANDSAT-8'
    f = MYFTP(hostaddr, username, password, '', dirparser=parse_unix)
    filelist = []
    f_handle = open('list.txt', 'r+')
    for line in f_handle:
        mtlFile = line.strip()
        fileUrl = 'ftp://'+hostaddr+'/'+mtlFile
        HOST = os.path.basename(urllib.parse.urlsplit(fileUrl)[1])
        DIRN = os.path.dirname(urllib.parse.urlsplit(fileUrl)[2])
        FILE = os.path.basename(urllib.parse.urlsplit(fileUrl)[2])
        try:
            f.download_file('C:\\software\\mtl\\'+FILE, mtlFile)
        except Exception as e:
            print(e)
    f_handle.close()

  
def test2():
    hostaddr = '10.6.8.80'
    username = 'sjg_user'
    password = 'x7Y#jPkbF9'
    remotedir = 'DOWNLOAD/LANDSAT-8'
    outputFolder = r'E:\landsat8-2014'
    f = MYFTP(hostaddr, username, password, '', dirparser=parse_unix)
    filepathDict = {}
    f_handle = open(r'C:\software\list_all.txt', 'r+')
    for line in f_handle:
        line = line.strip()
        filename = line.rsplit(sep='/', maxsplit=1)[-1]
        filepathDict[filename] = line
    f_handle.close()
    
    f_handle = open(r'C:\software\2014.txt', 'r+')
    for line in f_handle:
        line = line.strip()
        strList = line.split(sep='\t')
        if len(strList) < 10:
            continue
        localFilePath = strList[3]
        filename = localFilePath.rsplit(sep='/', maxsplit=1)[-1]
        ftpFilePath = filepathDict[filename]
        remoteFolder = ftpFilePath.rsplit(sep='/', maxsplit=1)[0]
        folderName = remoteFolder.rsplit(sep='/', maxsplit=1)[-1]
        iOutputFolder = outputFolder + '/' + folderName
        if not os.path.exists(iOutputFolder):
            os.makedirs(iOutputFolder)
        try:
            f.download_files(iOutputFolder, remoteFolder)
            f.connection.cwd('/')
            debug_print(u'返回目录 %s' %f.connection.pwd())
            #f.connection.cwd('..')
            #f.connection.cwd('..')
            #f.connection.cwd('..')
        except Exception as e:
            print(e)
    f_handle.close()
    
if __name__ == '__main__':
    test2()

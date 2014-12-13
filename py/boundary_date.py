#coding=utf-8 
#! python
#-*- coding:utf-8 -*-

import os
import sys
import string
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

ordinary_year_dayList = [0,31,59,90,120,151,181,212,243,273,304,334]
leap_year_dayList = [0,31,60,91,121,152,182,213,244,274,305,335]

def julian2date(year, julian_day):
    month = 1
    day = 1
    import calendar
    if calendar.isleap(year):
        for month in range(0, len(leap_year_dayList)):
            if julian_day <= leap_year_dayList[month]:
                day = julian_day - leap_year_dayList[month-1]
                return month,day
        month += 1
        day = julian_day - leap_year_dayList[month-1]
    else:
        for month in range(0, len(ordinary_year_dayList)):
            if julian_day <= ordinary_year_dayList[month]:
                day = julian_day - ordinary_year_dayList[month-1]
                return month,day
        month += 1
        day = julian_day - ordinary_year_dayList[month-1]
    return month,day


def parse_date_from_basename(basename):
    year = 2000
    month = 1
    day = 1
    strList = basename.split('-')
    if len(strList) > 4:
        # Landsat-5, Landsat7
        date = strList[4]
        year = int(date[0:4])
        month = int(date[4:6])
        day = int(date[6:8])
    elif len(strList) == 1:
        # Landat-8
        # LC81060292013221BJC00_MTL
        year = int(strList[0][9:13])
        julian_day = int(strList[0][13:16])
        month,day = julian2date(year, julian_day)
    return year,month,day

def boundary_date(imageFile, outFile):
    ds=gdal.Open(imageFile)
    
    gt=ds.GetGeoTransform()
    cols = ds.RasterXSize
    rows = ds.RasterYSize
    ext=GetExtent(gt,cols,rows)
    
    src_srs=osr.SpatialReference()
    src_srs.ImportFromWkt(ds.GetProjection())
    tgt_srs = src_srs.CloneGeogCS()
    
    geo_ext=ReprojectCoords(ext,src_srs,tgt_srs)
    maxLonLat =  max(geo_ext)
    minLonLat =  min(geo_ext)    
    
    north=40
    south=30
    west=-80
    east=-70    
    north = maxLonLat[1]
    south = minLonLat[1]
    west = minLonLat[0]
    east = maxLonLat[0]
    
    basename = os.path.basename(imageFile)
    year,month,day = parse_date_from_basename(basename)
    
    f = open(outFile, 'wb')
    f.write('north=%lf\n' %north)
    f.write('south=%lf\n' %south)
    f.write('west=%lf\n' %west)
    f.write('east=%lf\n' %east)
    f.write('year=%d\n' %year)
    f.write('month=%d\n' %month)
    f.write('day=%d\n' %day)
    f.close()
  
def main(argv):
    ##unit test
    #year = 2001
    #f_handle = open('test.txt', 'w+')
    #for i in range(1,367):
    #    month = 1
    #    day = 1
    #    month, day = julian2date(year, i)
    #    print('year=%d, month=%d, day=%d'%(year, month,day))    
    #f_handle.close()
    
    argv = gdal.GeneralCmdLineProcessor( argv )
    if argv is None:
        return Usage()
    imageFile = ''
    outFile = ''
    i = 1
    argc = len(argv)
    while i < argc:
        if argv[i] == '-i':
            imageFile = argv[i+1]
            i = i + 1
        elif argv[i] == '-o':
            outFile = argv[i+1]
            i = i + 1
        else:
            sys.stderr.write('Unexpected option : %s\n' % argv[i])
            return Usage()
                      
        i = i + 1
    if imageFile == '':
        sys.stderr.write('imageFile cannot be empty.\n')
        return Usage()
      
    if outFile == '':
        new_extension = '.txt'
        (outFile, ext) = os.path.splitext(imageFile)
        outFile = outFile + new_extension
        #os.rename(outFile, outFile + new_extension)
      
    boundary_date(imageFile, outFile)
      
      

def Usage():
    print('Usage: boundary_date -i imgFile [-o outFile]')
    return -1

if __name__ == '__main__':
    sys.exit(main(sys.argv))
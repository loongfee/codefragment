#!/bin/bash
# Modify the line above to the location of your BASH interpreter.
# BASH is an open source command line interpreter that is available
# for all UNIX platforms, LINUX, BSD and Mac OS X.
# Note that for running this script on Windows, you need to install
# a UNIX-environment on Windows such as CygWin (www.cygwin.com).


# process a fold
function fold_batch()
{	
	dirName=$(basename `pwd`)
	LSTTool -f '*'LST_Day_1km.tif -nv 0 -cutline ../$1 ../${dirName}.tif
}


for file in ./*
do
	if [ -d ${file} ]
		then
		cd ${file}
		fold_batch ../bnd1.shp
		cd ..
	fi
done

exit 0

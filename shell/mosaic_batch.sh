#!/bin/bash
# Modify the line above to the location of your BASH interpreter.
# BASH is an open source command line interpreter that is available
# for all UNIX platforms, LINUX, BSD and Mac OS X.
# Note that for running this script on Windows, you need to install
# a UNIX-environment on Windows such as CygWin (www.cygwin.com).


# process a fold
function fold_batch()
{	
	#ls *.hdf
	# Make a list of dates for processing
	# 文件前缀
	file_prefix=“”
	declare -a DATELIST
	HDFFILES=$(ls *.hdf)

	for FILE in $HDFFILES
	do
		# 对.进行分割
		IFS='.' fsplit=($FILE)
		# 分割结果元素个数太小则略过
		if [ ${#fsplit[@]} -lt 5 ]
			then 
			continue
		fi
		# 提取日期
		d=${fsplit[1]:1}
		# 自动去掉重复的日期
		DATELIST[$d]=$d
		# 文件前缀
		file_prefix=${fsplit[0]}
	done

	#取消分割
	unset IFS
	#Loop through the number of dates
	for DATE in ${DATELIST[@]}
	do
		# if the result file exists, 
		if [ -e ${file_prefix}_$DATE*.tif ]
			then
			#echo "exist"
			continue
		fi
		# Collect all MOD15 HDF files for a specific date
		HDFFILES=$(ls ${file_prefix}.A$DATE.*.hdf)
		#echo $HDFFILES
		#exit 0
		# Write these to a text file
		echo $HDFFILES > mosaicinput.txt
		# Run mrt mosaic and write output to HDF file (extension .hdf!)
		mrtmosaic -i mosaicinput.txt -o mosaic_tmp.hdf
		# Call resample. Values for projection parameters are derived
		# from the prm-file that was obtained using ModisTool. Input and
		# output are specified using the -i and -o options.
		resample -p $1 -i mosaic_tmp.hdf -o ${file_prefix}_$DATE.tif
		#resample -p predef.prm -i mosaic_tmp.hdf -o ${file_prefix}_$DATE.tif

		# 删除临时文件
		rm -f mosaicinput.txt
		rm -f mosaic_tmp.hdf
		rm -f rm -f *.log
	done
}

fold_batch "predef.prm"

for file in ./*
do
	if [ -d ${file} ]
		then
		cd ${file}
		fold_batch "../predef.prm"
		cd ..
	fi
done

exit 0

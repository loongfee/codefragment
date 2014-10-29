#!/bin/bash

tiflist=$(ls *.tif)
num=${#tiflist[@]}
counter=1
for file in ${tiflist}
do
	# 对_进行分割
	# 保存原始分隔符（空格,tab,和新行）
	OLD_IFS=$IFS
	# 对新分隔符进行分割
	IFS='_'
	# 保存分割结果到strList，以空格隔开
	oldName=($file)		# 注意：分割字符串赋值需要加"()"。
	# 还原分隔符
	IFS=$OLD_IFS
	newName=${oldName[1]}'.hgt'
	echo ${num}'...'
	gdal_translate -of SRTMHGT ${file} ${newName}
	num=$(($num+1))
done

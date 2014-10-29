#!/bin/bash

for file in ./*
do
	if [ -d ${file} ]
		then
		cd ${file}
		# gdal_translate -of JPEG -b 1 -b 2 -b 3 -outsize 25% 25% IMAGE.TIF thumbnail.jpg
		gdal_translate -of JPEG -b 1 -b 2 -b 3 -outsize 1024 1024 IMAGE.TIF thumbnail.jpg
		cd ..
	fi
done

exit 0
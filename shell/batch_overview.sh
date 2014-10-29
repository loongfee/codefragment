#!/bin/bash

for file in ./*
do
	if [ -d ${file} ]
		then
		cd ${file}
		ossim-img2rr.exe -r IMAGE.TIF
		cd ..
	fi
done

exit 0
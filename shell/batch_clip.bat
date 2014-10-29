@echo off
REM 要查找的文件
SetLocal EnableDelayedExpansion

REM set ext=*.rm,*.rmvb,*.avi,*.mkv,*.torrent
set ext=*.tif

REM 遍历文件，并截取编号作为新文件名
for %%a in (!ext!) do (

REM 文件名
set fn=%%~na

REM 后缀
set en=%%~xa

REM 取 pstart 位置之后的所有字符 !fn:~%pstart%!!en!
REM 取文件名最后 length 长度字符 !fn:~-%length%!!en!
REM 取文件名 pstart 开始的 length 长度字符 !fn:~%pstart%,%length%!!en!

REM 显示新文件名
raster_clip.exe -i %%a -o ..\clip\!fn!.tif -shp bnd_ll.shp -field ENTIID -value 武汉

REM 修改文件名
REM rename "%%a" "!fn:~%pstart%,%length%!!en!"
)
@echo off
REM Ҫ���ҵ��ļ�
SetLocal EnableDelayedExpansion

REM set ext=*.rm,*.rmvb,*.avi,*.mkv,*.torrent
set ext=*.tif

REM �����ļ�������ȡ�����Ϊ���ļ���
for %%a in (!ext!) do (

REM �ļ���
set fn=%%~na

REM ��׺
set en=%%~xa

REM ȡ pstart λ��֮��������ַ� !fn:~%pstart%!!en!
REM ȡ�ļ������ length �����ַ� !fn:~-%length%!!en!
REM ȡ�ļ��� pstart ��ʼ�� length �����ַ� !fn:~%pstart%,%length%!!en!

REM ��ʾ���ļ���
raster_clip.exe -i %%a -o ..\clip\!fn!.tif -shp bnd_ll.shp -field ENTIID -value �人

REM �޸��ļ���
REM rename "%%a" "!fn:~%pstart%,%length%!!en!"
)
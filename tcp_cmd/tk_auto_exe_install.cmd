rd /s /q dist

pyinstaller tk_auto.py

del /f /q *.spec
rd /s /q build
rd /s /q __pycache__

mkdir .\dist\tk_auto\00_set 
mkdir .\dist\tk_auto\01_template
mkdir  .\dist\tk_auto\02_result

copy 00_set .\dist\tk_auto\00_set
copy 01_template .\dist\tk_auto\01_template
copy 02_result .\dist\tk_auto\02_result

cd .\dist\tk_auto
del /f /q mkl_*.dll

pause 

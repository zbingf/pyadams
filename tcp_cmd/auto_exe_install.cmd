rd /s /q dist

pyinstaller auto.py

del /f /q *.spec
rd /s /q build
rd /s /q __pycache__

mkdir .\dist\auto\00_set 
mkdir .\dist\auto\01_template
mkdir  .\dist\auto\02_result

copy 00_set .\dist\auto\00_set
copy 01_template .\dist\auto\01_template
copy 02_result .\dist\auto\02_result

cd .\dist\auto
del /f /q mkl_*.dll

pause 

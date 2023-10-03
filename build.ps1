$Today = Get-Date -Format "yyMMddTHHmmss"
$TargetDir = ".\dist\a-$Today"

#Remove-Item -Path $TargetDir -Recurse

## build by nuitka
#.\venv\Scripts\nuitka.bat --onefile --enable-plugin=tk-inter --include-data-dir=./assets/=assets .\src\app.py
.\venv\Scripts\nuitka.bat --onefile --enable-plugin=tk-inter --include-data-dir=./assets/=assets --windows-icon-from-ico=./assets/logo-leaf.png .\src\app.py
#.\venv\Scripts\nuitka.bat --onefile --enable-plugin=tk-inter --include-data-dir=./assets/=assets .\src\app.py

# --windows-icon-from-ico=ct-logo.png
## not support MinGW64, only support for MSVC
#--onefile-windows-splash-screen-image=assets\landing_bg.png

## build by pyinstaller
#pyinstaller.exe --onefile -F .\src\app.py -p .\ --clean

New-Item -Path $TargetDir -ItemType Directory
#Move-Item -Path .\dist\app.exe -Destination $TargetDir
Move-Item -Path .\app.exe -Destination $TargetDir
Copy-Item -Path .\assets -Recurse -Destination $TargetDir
Copy-Item -Path .\dist\config.ini.dist -Destination "$TargetDir\config.ini"

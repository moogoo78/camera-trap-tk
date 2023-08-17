$Today = Get-Date -Format "yyMMddTHHmmss"
$TargetDir = ".\dist\a-$Today"

#poetry.exe run pyinstaller.exe --onefile -F .\src\app.py --clean
#Remove-Item -Path $TargetDir -Recurse

.\venv\Scripts\nuitka.bat --onefile --enable-plugin=tk-inter --windows-icon-from-ico=ct-logo.png --include-data-dir=./assets/=assets .\src\app.py

#--onefile-windows-splash-screen-image=13317.jpg

New-Item -Path $TargetDir -ItemType Directory
Move-Item -Path .\app.exe -Destination $TargetDir
Copy-Item -Path .\assets -Recurse -Destination $TargetDir
Copy-Item -Path .\dist\config.ini.dist -Destination "$TargetDir\config.ini"

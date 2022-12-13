$Today = Get-Date -Format "yyMMddTHHmmss"
$TargetDir = ".\dist\a-$Today"

poetry.exe run pyinstaller.exe --onefile -F .\src\app.py --clean

#Remove-Item -Path $TargetDir -Recurse

New-Item -Path $TargetDir -ItemType Directory
Move-Item -Path .\dist\app.exe -Destination $TargetDir
Copy-Item -Path .\assets -Recurse -Destination $TargetDir
Copy-Item -Path .\dist\config.ini.dist -Destination "$TargetDir\config.ini"

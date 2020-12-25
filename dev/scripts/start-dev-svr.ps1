$CWD = Get-Location

$pyFolder = Join-Path -Path $CWD -ChildPath "mealie"
$pyVenv = Join-Path -Path $CWD -ChildPath "/venv/Scripts/python.exe"
$pyScript = Join-Path -Path $CWD -ChildPath "/mealie/app.py"

$pythonCommand = "powershell.exe -NoExit -Command  $pyVenv $pyScript"

$vuePath = Join-Path -Path $CWD -ChildPath "/frontend"
$npmCommand = "powershell.exe -NoExit -Command npm run serve"

wt -d $pyFolder "powershell.exe" $pythonCommand `; split-pane -d $vuePath "powershell.exe" $npmCommand

Start-Process chrome "http://127.0.0.1:8000/docs"
Start-Process chrome "http://127.0.0.1:8080
"


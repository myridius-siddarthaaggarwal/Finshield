param (
    [string]$Message = "",
    [string]$Remote = "origin",
    [switch]$NoVerify = $false
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $ScriptDir

$PythonExe = Join-Path $ScriptDir ".venv\Scripts\python.exe"
if (-not (Test-Path $PythonExe)) {
    $PythonExe = "python"
}

$GitAgentPy = Join-Path $ScriptDir "agents\git_agent\git_agent.py"

$ArgsList = @($GitAgentPy, "autopush", "--remote", $Remote)
if ($Message -ne "") {
    $ArgsList += @("-m", $Message)
}
if ($NoVerify) {
    $ArgsList += @("--no-verify")
}

& $PythonExe $ArgsList

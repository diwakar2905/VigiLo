# Run as Administrator

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "WatchDog" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check admin
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
  Write-Host "[ERROR] This script must be run as Administrator!" -ForegroundColor Red
  pause
  exit
}

# Dynamic path resolution
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$rootPath = Split-Path -Parent $scriptPath
$exePath = Join-Path $rootPath "dist\WatchDog.exe"
$workingDir = Join-Path $rootPath "dist"
$currentUser = [Security.Principal.WindowsIdentity]::GetCurrent().Name

Write-Host "Paths:" -ForegroundColor Gray
Write-Host "  Root: $rootPath" -ForegroundColor Gray
Write-Host "  Exe:  $exePath" -ForegroundColor Gray
Write-Host "  User: $currentUser" -ForegroundColor Gray
Write-Host ""

# Enable Audit Policy (Critical for Event 4625)
Write-Host "Enabling Audit Policy (Logon Failures)..." -ForegroundColor Yellow
auditpol /set /subcategory:"Logon" /failure:enable
if ($LASTEXITCODE -eq 0) {
  Write-Host "[SUCCESS] Audit Policy Enabled" -ForegroundColor Green
}
else {
  Write-Host "[WARNING] Could not set Audit Policy. Manual enable required." -ForegroundColor Red
}
Write-Host ""

# Stop running instances
Write-Host "Stopping running instances..." -ForegroundColor Yellow
Stop-Process -Name WatchDog -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Cleanup old tasks
Write-Host "Removing old tasks..." -ForegroundColor Yellow
schtasks /Delete /TN "AntiTheft_Service" /F 2>$null | Out-Null
schtasks /Delete /TN "AntiTheft_Commander" /F 2>$null | Out-Null
# Remove legacy task name if exists
schtasks /Delete /TN "WatchDogMonitor" /F 2>$null | Out-Null

# ---------------------------------------------------------------------------
# TASK 1: SERVICE (System, Boot, Security Monitor)
# ---------------------------------------------------------------------------
$xmlService = @"
<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>Anti-Theft Security Service (System Watcher)</Description>
  </RegistrationInfo>
  <Triggers>
    <BootTrigger>
      <Enabled>true</Enabled>
    </BootTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>S-1-5-18</UserId>
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>true</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <DisallowStartOnRemoteAppSession>false</DisallowStartOnRemoteAppSession>
    <UseUnifiedSchedulingEngine>true</UseUnifiedSchedulingEngine>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <Priority>7</Priority>
    <RestartOnFailure>
      <Interval>PT1M</Interval>
      <Count>999</Count>
    </RestartOnFailure>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>$exePath</Command>
      <Arguments>--service</Arguments>
      <WorkingDirectory>$workingDir</WorkingDirectory>
    </Exec>
  </Actions>
</Task>
"@

# ---------------------------------------------------------------------------
# TASK 2: COMMANDER (User, Logon, Telegram Agent)
# ---------------------------------------------------------------------------
$xmlCommander = @"
<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>Anti-Theft Commander (User Agent)</Description>
  </RegistrationInfo>
  <Triggers>
    <LogonTrigger>
      <Enabled>true</Enabled>
    </LogonTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>$currentUser</UserId>
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>true</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <DisallowStartOnRemoteAppSession>false</DisallowStartOnRemoteAppSession>
    <UseUnifiedSchedulingEngine>true</UseUnifiedSchedulingEngine>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <Priority>7</Priority>
    <RestartOnFailure>
      <Interval>PT1M</Interval>
      <Count>999</Count>
    </RestartOnFailure>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>$exePath</Command>
      <Arguments>--commander</Arguments>
      <WorkingDirectory>$workingDir</WorkingDirectory>
    </Exec>
  </Actions>
</Task>
"@

# Save and Register Service
$xmlPathService = Join-Path $env:TEMP "antitheft_service.xml"
$xmlService | Out-File -FilePath $xmlPathService -Encoding unicode
Write-Host "Creating Service Task (SYSTEM/Boot)..." -ForegroundColor Cyan
schtasks /Create /TN "AntiTheft_Service" /XML $xmlPathService /F

# Save and Register Commander
$xmlPathCommander = Join-Path $env:TEMP "antitheft_commander.xml"
$xmlCommander | Out-File -FilePath $xmlPathCommander -Encoding unicode
Write-Host "Creating Commander Task (User/Logon)..." -ForegroundColor Cyan
schtasks /Create /TN "AntiTheft_Commander" /XML $xmlPathCommander /F

# Clean up
Remove-Item $xmlPathService -ErrorAction SilentlyContinue
Remove-Item $xmlPathCommander -ErrorAction SilentlyContinue

# Verify
Write-Host ""
Write-Host "Verifying tasks..." -ForegroundColor Yellow
schtasks /Query /TN "AntiTheft_Service" /V /FO LIST 2>&1 | Select-String "Task Name|Status|Task To Run|Run As User"
schtasks /Query /TN "AntiTheft_Commander" /V /FO LIST 2>&1 | Select-String "Task Name|Status|Task To Run|Run As User"

# Start them
Write-Host ""
Write-Host "Starting tasks..." -ForegroundColor Yellow
schtasks /Run /TN "AntiTheft_Service" | Out-Null
schtasks /Run /TN "AntiTheft_Commander" | Out-Null
Start-Sleep -Seconds 3

# Check processes
$procs = Get-Process -Name WatchDog -ErrorAction SilentlyContinue
if ($procs) {
  Write-Host "[SUCCESS] $($procs.Count) Monitor Instance(s) Running" -ForegroundColor Green
  $procs | Format-Table Id, ProcessName, StartTime, MainWindowTitle -AutoSize
}
else {
  Write-Host "[WARNING] No monitor processes found." -ForegroundColor Yellow
}

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Setup Complete." -ForegroundColor Green
Write-Host "  Service: Runs at Boot (Lock Screen Protection) - SYSTEM" -ForegroundColor White
Write-Host "  Commander: Runs at Login (Screenshots/Lock) - $currentUser" -ForegroundColor White
Write-Host "================================================" -ForegroundColor Cyan
pause

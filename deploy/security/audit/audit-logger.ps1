# Audit Logger Script for Windows
# This script provides basic audit logging functionality

param(
    [string]$Action,
    [string]$User = $env:USERNAME,
    [string]$Resource,
    [string]$Details
)

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$logEntry = "$timestamp | $Action | $User | $Resource | $Details"

# Ensure log directory exists
$logDir = "security/logs"
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

# Log to file
$logFile = "$logDir/audit.log"
$logEntry | Out-File -FilePath $logFile -Append -Encoding UTF8

# Log to Windows Event Log (requires admin privileges)
try {
    # Create event source if it doesn't exist
    if (-not [System.Diagnostics.EventLog]::SourceExists("Django-GraphQL-Security")) {
        New-EventLog -LogName "Application" -Source "Django-GraphQL-Security"
    }
    
    Write-EventLog -LogName "Application" -Source "Django-GraphQL-Security" -EventId 1001 -EntryType Information -Message $logEntry
} catch {
    Write-Warning "Could not write to Windows Event Log: $_"
}

Write-Host "Audit log entry created: $logEntry"

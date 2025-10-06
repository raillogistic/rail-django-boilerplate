# Security Setup Script for Django GraphQL Boilerplate (Windows PowerShell)
# This script automates the setup of security configurations for production deployment

param(
    [switch]$Force,
    [switch]$SkipSSL,
    [switch]$Help
)

# Error handling
$ErrorActionPreference = "Stop"

# Colors for output (PowerShell compatible)
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-ColorOutput "[$timestamp] $Message" -Color "Blue"
}

function Write-Error-Custom {
    param([string]$Message)
    Write-ColorOutput "[ERROR] $Message" -Color "Red"
}

function Write-Success {
    param([string]$Message)
    Write-ColorOutput "[SUCCESS] $Message" -Color "Green"
}

function Write-Warning-Custom {
    param([string]$Message)
    Write-ColorOutput "[WARNING] $Message" -Color "Yellow"
}

# Help function
function Show-Help {
    Write-Host @"
Security Setup Script for Django GraphQL Boilerplate

USAGE:
    .\security-setup.ps1 [OPTIONS]

OPTIONS:
    -Force      Force overwrite existing configurations
    -SkipSSL    Skip SSL certificate setup
    -Help       Show this help message

DESCRIPTION:
    This script automates the security setup for production deployment including:
    - Directory creation and permissions
    - Secret generation
    - SSL certificate setup (if not skipped)
    - Security service configuration
    - Fail2ban setup
    - Audit logging configuration

REQUIREMENTS:
    - PowerShell 5.0 or higher
    - Docker and Docker Compose installed
    - Administrative privileges for some operations

EXAMPLES:
    .\security-setup.ps1
    .\security-setup.ps1 -Force
    .\security-setup.ps1 -SkipSSL
"@
}

if ($Help) {
    Show-Help
    exit 0
}

# Generate secure random string
function New-SecureRandomString {
    param(
        [int]$Length = 32,
        [switch]$IncludeSpecialChars
    )
    
    $chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    if ($IncludeSpecialChars) {
        $chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"
    }
    
    $random = New-Object System.Random
    $result = ""
    for ($i = 0; $i -lt $Length; $i++) {
        $result += $chars[$random.Next(0, $chars.Length)]
    }
    
    return $result
}

# Load environment variables from .env.production file
function Import-EnvironmentFile {
    param([string]$FilePath = ".env.production")
    
    if (-not (Test-Path $FilePath)) {
        Write-Warning-Custom ".env.production file not found. Using default values for demo."
        return
    }
    
    Write-Log "Loading environment variables from $FilePath..."
    
    Get-Content $FilePath | ForEach-Object {
        if ($_ -match '^([^#][^=]+)=(.*)$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            
            # Remove quotes if present
            if ($value -match '^"(.*)"$' -or $value -match "^'(.*)'$") {
                $value = $matches[1]
            }
            
            [System.Environment]::SetEnvironmentVariable($name, $value, "Process")
        }
    }
}

# Check required environment variables
function Test-EnvironmentVariables {
    $requiredVars = @(
        "DOMAIN_NAME",
        "SSL_EMAIL", 
        "POSTGRES_PASSWORD",
        "JWT_SECRET_KEY",
        "SECRET_KEY"
    )
    
    $missingVars = @()
    
    foreach ($var in $requiredVars) {
        $value = [System.Environment]::GetEnvironmentVariable($var)
        if (-not $value -or $value -eq "") {
            $missingVars += $var
        }
    }
    
    if ($missingVars.Count -gt 0) {
        Write-Warning-Custom "Some required environment variables are missing: $($missingVars -join ', ')"
        Write-Warning-Custom "Using generated default values for demo purposes."
        
        # Set default values for missing variables
        foreach ($var in $missingVars) {
            switch ($var) {
                "DOMAIN_NAME" { [System.Environment]::SetEnvironmentVariable($var, "localhost", "Process") }
                "SSL_EMAIL" { [System.Environment]::SetEnvironmentVariable($var, "admin@localhost", "Process") }
                "POSTGRES_PASSWORD" { [System.Environment]::SetEnvironmentVariable($var, (New-SecureRandomString -Length 16), "Process") }
                "JWT_SECRET_KEY" { [System.Environment]::SetEnvironmentVariable($var, (New-SecureRandomString -Length 32), "Process") }
                "SECRET_KEY" { [System.Environment]::SetEnvironmentVariable($var, (New-SecureRandomString -Length 50), "Process") }
            }
        }
        Write-Success "Default values set for missing environment variables."
    }
    
    return $true
}

# Create directory structure
function New-SecurityDirectories {
    Write-Log "Creating security directory structure..."
    
    $directories = @(
        "security/ssl",
        "security/logs", 
        "security/fail2ban",
        "security/promtail",
        "security/audit",
        "volumes/prometheus",
        "volumes/grafana",
        "volumes/nginx/ssl",
        "volumes/backup"
    )
    
    foreach ($dir in $directories) {
        $fullPath = Join-Path $PWD $dir
        if (-not (Test-Path $fullPath)) {
            New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
            Write-Success "Created directory: $dir"
        } else {
            Write-Warning-Custom "Directory already exists: $dir"
        }
    }
}

# Generate secrets
function New-SecuritySecrets {
    Write-Log "Generating security secrets..."
    
    $secretsFile = "security/.secrets"
    
    if ((Test-Path $secretsFile) -and -not $Force) {
        Write-Warning-Custom "Secrets file already exists. Use -Force to overwrite."
        return
    }
    
    $secrets = @{
        "DJANGO_SECRET_KEY" = New-SecureRandomString -Length 50 -IncludeSpecialChars
        "JWT_SECRET_KEY" = New-SecureRandomString -Length 64
        "POSTGRES_PASSWORD" = New-SecureRandomString -Length 32
        "REDIS_PASSWORD" = New-SecureRandomString -Length 32
        "GRAFANA_ADMIN_PASSWORD" = New-SecureRandomString -Length 16
        "BACKUP_ENCRYPTION_KEY" = New-SecureRandomString -Length 32
    }
    
    $secretsContent = @()
    $secretsContent += "# Generated secrets - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    $secretsContent += "# DO NOT COMMIT THIS FILE TO VERSION CONTROL"
    $secretsContent += ""
    
    foreach ($key in $secrets.Keys) {
        $secretsContent += "$key=$($secrets[$key])"
    }
    
    $secretsContent | Out-File -FilePath $secretsFile -Encoding UTF8
    
    # Set restrictive permissions (Windows equivalent)
    try {
        $acl = Get-Acl $secretsFile
        $acl.SetAccessRuleProtection($true, $false)
        $accessRule = New-Object System.Security.AccessControl.FileSystemAccessRule(
            [System.Security.Principal.WindowsIdentity]::GetCurrent().Name,
            "FullControl",
            "Allow"
        )
        $acl.SetAccessRule($accessRule)
        Set-Acl -Path $secretsFile -AclObject $acl
    } catch {
        Write-Warning-Custom "Could not set restrictive permissions on secrets file: $_"
    }
    
    Write-Success "Generated secrets file: $secretsFile"
}

# Setup SSL certificates (placeholder for Windows)
function Set-SSLCertificates {
    if ($SkipSSL) {
        Write-Warning-Custom "Skipping SSL certificate setup"
        return
    }
    
    Write-Log "Setting up SSL certificate configuration..."
    
    $sslDir = "security/ssl"
    $certbotConfig = @"
# SSL Certificate Setup for Windows

For Windows deployment, consider using one of these options:

1. **win-acme (Recommended for Let's Encrypt)**
   - Download from: https://www.win-acme.com/
   - Example command: wacs.exe --target manual --host $env:DOMAIN_NAME --emailaddress $env:SSL_EMAIL

2. **Manual Certificate Installation**
   - Obtain certificates from your certificate authority
   - Place certificate files in this directory:
     - certificate.crt (your domain certificate)
     - private.key (private key)
     - ca_bundle.crt (certificate authority bundle)

3. **Cloud Provider SSL Certificates**
   - AWS Certificate Manager (ACM)
   - Azure Key Vault
   - Google Cloud SSL Certificates

4. **Self-Signed Certificates (Development Only)**
   - Use OpenSSL or PowerShell to generate self-signed certificates
   - NOT recommended for production use

After obtaining certificates, update the nginx configuration in docker-compose.production.yml
to reference the correct certificate paths.
"@
    
    $certbotConfig | Out-File -FilePath "$sslDir/README.txt" -Encoding UTF8
    Write-Success "Created SSL setup instructions: $sslDir/README.txt"
}

# Configure Fail2ban (Windows equivalent using Windows Firewall)
function Set-Fail2banConfig {
    Write-Log "Configuring intrusion prevention..."
    
    $fail2banDir = "security/fail2ban"
    $windowsFirewallScript = @"
# Windows Firewall Security Script
# This script provides basic intrusion prevention using Windows Firewall
# Run as Administrator

# Enable Windows Firewall for all profiles
Write-Host "Enabling Windows Firewall..."
netsh advfirewall set allprofiles state on

# Block common attack ports
Write-Host "Blocking common attack ports..."
netsh advfirewall firewall add rule name="Block Telnet" dir=in action=block protocol=TCP localport=23
netsh advfirewall firewall add rule name="Block FTP" dir=in action=block protocol=TCP localport=21
netsh advfirewall firewall add rule name="Block TFTP" dir=in action=block protocol=UDP localport=69
netsh advfirewall firewall add rule name="Block NetBIOS" dir=in action=block protocol=TCP localport=139
netsh advfirewall firewall add rule name="Block SMB" dir=in action=block protocol=TCP localport=445

# Allow only necessary ports for web services
Write-Host "Allowing necessary web service ports..."
netsh advfirewall firewall add rule name="Allow HTTP" dir=in action=allow protocol=TCP localport=80
netsh advfirewall firewall add rule name="Allow HTTPS" dir=in action=allow protocol=TCP localport=443

# Enable logging for security monitoring
Write-Host "Enabling firewall logging..."
netsh advfirewall set allprofiles logging droppedconnections enable
netsh advfirewall set allprofiles logging allowedconnections enable
netsh advfirewall set allprofiles logging filename "%systemroot%\system32\LogFiles\Firewall\pfirewall.log"

Write-Host "Windows Firewall configured for basic intrusion prevention"
Write-Host "Log file location: %systemroot%\system32\LogFiles\Firewall\pfirewall.log"
"@
    
    $windowsFirewallScript | Out-File -FilePath "$fail2banDir/windows-firewall-setup.ps1" -Encoding UTF8
    Write-Success "Created Windows Firewall configuration: $fail2banDir/windows-firewall-setup.ps1"
}

# Configure Promtail for log monitoring
function Set-PromtailConfig {
    Write-Log "Configuring log monitoring..."
    
    $promtailDir = "security/promtail"
    $promtailConfig = @"
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: django-logs
    static_configs:
      - targets:
          - localhost
        labels:
          job: django
          __path__: /var/log/django/*.log

  - job_name: nginx-logs
    static_configs:
      - targets:
          - localhost
        labels:
          job: nginx
          __path__: /var/log/nginx/*.log

  - job_name: security-logs
    static_configs:
      - targets:
          - localhost
        labels:
          job: security
          __path__: /var/log/security/*.log

  - job_name: windows-eventlog
    windows_events:
      use_incoming_timestamp: false
      bookmark_path: "./bookmark.xml"
      poll_interval: 3s
      eventlog_name: "Application"
      xpath_query: '*[System[Provider[@Name="Django-GraphQL-Security"]]]'
      labels:
        job: windows-security
        host: localhost
"@
    
    $promtailConfig | Out-File -FilePath "$promtailDir/promtail.yml" -Encoding UTF8
    Write-Success "Created Promtail configuration: $promtailDir/promtail.yml"
}

# Create audit logger
function New-AuditLogger {
    Write-Log "Setting up audit logging..."
    
    $auditDir = "security/audit"
    $auditScript = @"
# Audit Logger Script for Windows
# This script provides basic audit logging functionality

param(
    [string]`$Action,
    [string]`$User = `$env:USERNAME,
    [string]`$Resource,
    [string]`$Details
)

`$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
`$logEntry = "`$timestamp | `$Action | `$User | `$Resource | `$Details"

# Ensure log directory exists
`$logDir = "security/logs"
if (-not (Test-Path `$logDir)) {
    New-Item -ItemType Directory -Path `$logDir -Force | Out-Null
}

# Log to file
`$logFile = "`$logDir/audit.log"
`$logEntry | Out-File -FilePath `$logFile -Append -Encoding UTF8

# Log to Windows Event Log (requires admin privileges)
try {
    # Create event source if it doesn't exist
    if (-not [System.Diagnostics.EventLog]::SourceExists("Django-GraphQL-Security")) {
        New-EventLog -LogName "Application" -Source "Django-GraphQL-Security"
    }
    
    Write-EventLog -LogName "Application" -Source "Django-GraphQL-Security" -EventId 1001 -EntryType Information -Message `$logEntry
} catch {
    Write-Warning "Could not write to Windows Event Log: `$_"
}

Write-Host "Audit log entry created: `$logEntry"
"@
    
    $auditScript | Out-File -FilePath "$auditDir/audit-logger.ps1" -Encoding UTF8
    Write-Success "Created audit logger: $auditDir/audit-logger.ps1"
}

# Main execution
function Start-SecuritySetup {
    Write-Log "Starting security setup for Django GraphQL Boilerplate..."
    
    # Load environment variables from file
    Import-EnvironmentFile
    
    # Check prerequisites
    if (-not (Test-EnvironmentVariables)) {
        Write-Error-Custom "Environment validation failed. Please check your .env.production file."
        exit 1
    }
    
    try {
        # Create directory structure
        New-SecurityDirectories
        
        # Generate secrets
        New-SecuritySecrets
        
        # Setup SSL certificates
        Set-SSLCertificates
        
        # Configure security services
        Set-Fail2banConfig
        Set-PromtailConfig
        New-AuditLogger
        
        Write-Success "Security setup completed successfully!"
        Write-Log "Next steps:"
        Write-Host "  1. Review generated secrets in security/.secrets"
        Write-Host "  2. Configure SSL certificates (see security/ssl/README.txt)"
        Write-Host "  3. Run Windows Firewall setup as Administrator:"
        Write-Host "     PowerShell -ExecutionPolicy Bypass -File security/fail2ban/windows-firewall-setup.ps1"
        Write-Host "  4. Test the deployment with:"
        Write-Host "     docker-compose -f docker-compose.production.yml -f docker-compose.security.yml up -d"
        
    } catch {
        Write-Error-Custom "Security setup failed: $_"
        exit 1
    }
}

# Execute main function
Start-SecuritySetup
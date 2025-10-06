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

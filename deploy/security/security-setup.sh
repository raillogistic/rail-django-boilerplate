#!/bin/bash

# Security Setup Script for Django GraphQL Boilerplate
# This script automates the setup of security configurations for production deployment

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        error "This script should not be run as root for security reasons"
        exit 1
    fi
}

# Check required environment variables
check_env_vars() {
    local required_vars=(
        "DOMAIN_NAME"
        "SSL_EMAIL"
        "POSTGRES_PASSWORD"
        "JWT_SECRET_KEY"
        "SECRET_KEY"
    )
    
    local missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var:-}" ]]; then
            missing_vars+=("$var")
        fi
    done
    
    if [[ ${#missing_vars[@]} -gt 0 ]]; then
        error "Missing required environment variables:"
        printf '%s\n' "${missing_vars[@]}"
        exit 1
    fi
}

# Generate secure passwords and keys
generate_secrets() {
    log "Generating secure secrets..."
    
    # Generate JWT secret if not provided
    if [[ -z "${JWT_SECRET_KEY:-}" ]]; then
        export JWT_SECRET_KEY=$(openssl rand -base64 64 | tr -d '\n')
        success "Generated JWT secret key"
    fi
    
    # Generate Django secret key if not provided
    if [[ -z "${SECRET_KEY:-}" ]]; then
        export SECRET_KEY=$(openssl rand -base64 64 | tr -d '\n')
        success "Generated Django secret key"
    fi
    
    # Generate database password if not provided
    if [[ -z "${POSTGRES_PASSWORD:-}" ]]; then
        export POSTGRES_PASSWORD=$(openssl rand -base64 32 | tr -d '\n')
        success "Generated database password"
    fi
}

# Create necessary directories
create_directories() {
    log "Creating security directories..."
    
    local dirs=(
        "ssl/certbot/conf"
        "ssl/certbot/www"
        "ssl/certbot/logs"
        "fail2ban/data"
        "fail2ban/jail.d"
        "logs/audit"
        "logs/security"
        "security/trivy-cache"
        "monitoring/promtail"
    )
    
    for dir in "${dirs[@]}"; do
        mkdir -p "$dir"
        log "Created directory: $dir"
    done
    
    success "Security directories created"
}

# Set proper file permissions
set_permissions() {
    log "Setting secure file permissions..."
    
    # SSL directories
    chmod 700 ssl/
    chmod 755 ssl/certbot/www/
    
    # Log directories
    chmod 755 logs/
    chmod 750 logs/audit/
    chmod 750 logs/security/
    
    # Configuration files
    find . -name "*.yml" -exec chmod 644 {} \;
    find . -name "*.conf" -exec chmod 644 {} \;
    find . -name "*.sh" -exec chmod 755 {} \;
    
    # Environment files
    chmod 600 .env.prod 2>/dev/null || true
    
    success "File permissions set"
}

# Configure fail2ban
setup_fail2ban() {
    log "Setting up fail2ban configuration..."
    
    cat > fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5
backend = auto
usedns = warn
logencoding = auto
enabled = false
mode = normal
filter = %(__name__)s[mode=%(mode)s]

[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log
maxretry = 3
bantime = 86400

[nginx-http-auth]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 3

[nginx-limit-req]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 10

[nginx-botsearch]
enabled = true
port = http,https
logpath = /var/log/nginx/access.log
maxretry = 2
EOF
    
    success "Fail2ban configuration created"
}

# Setup SSL certificates
setup_ssl() {
    log "Setting up SSL certificates..."
    
    if [[ -z "${DOMAIN_NAME:-}" ]]; then
        warning "DOMAIN_NAME not set, skipping SSL setup"
        return 0
    fi
    
    # Create initial certificate request
    docker-compose -f docker-compose.production.yml -f docker-compose.security.yml \
        run --rm certbot certonly --webroot \
        --webroot-path=/var/www/certbot \
        --email "${SSL_EMAIL}" \
        --agree-tos \
        --no-eff-email \
        -d "${DOMAIN_NAME}" \
        --staging  # Remove --staging for production
    
    success "SSL certificate setup initiated"
}

# Create monitoring configuration
setup_monitoring() {
    log "Setting up security monitoring..."
    
    cat > monitoring/promtail.yml << 'EOF'
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: system
    static_configs:
      - targets:
          - localhost
        labels:
          job: varlogs
          __path__: /var/log/*log

  - job_name: nginx
    static_configs:
      - targets:
          - localhost
        labels:
          job: nginx
          __path__: /var/log/nginx/*.log

  - job_name: audit
    static_configs:
      - targets:
          - localhost
        labels:
          job: audit
          __path__: /var/log/audit/*.log
EOF
    
    success "Monitoring configuration created"
}

# Create security audit script
create_audit_script() {
    log "Creating security audit script..."
    
    cat > scripts/audit-logger.sh << 'EOF'
#!/bin/sh

# Security audit logger
# Monitors and logs security events

LOG_FILE="/var/log/audit/security.log"
PID_FILE="/tmp/audit-logger.pid"

# Create log file if it doesn't exist
touch "$LOG_FILE"

# Function to log events
log_event() {
    echo "$(date -Iseconds) [AUDIT] $1" >> "$LOG_FILE"
}

# Monitor for security events
monitor_security() {
    log_event "Security monitoring started"
    
    while true; do
        # Check for failed login attempts
        if [ -f /var/log/auth.log ]; then
            tail -n 100 /var/log/auth.log | grep -i "failed\|invalid\|authentication failure" | \
            while read -r line; do
                log_event "AUTH_FAILURE: $line"
            done
        fi
        
        # Check for suspicious network activity
        netstat -tuln | grep -E ":22|:80|:443" | \
        while read -r line; do
            log_event "NETWORK: $line"
        done
        
        sleep 60
    done
}

# Start monitoring
echo $$ > "$PID_FILE"
monitor_security
EOF
    
    chmod +x scripts/audit-logger.sh
    success "Security audit script created"
}

# Validate configuration
validate_config() {
    log "Validating security configuration..."
    
    # Check Docker Compose files
    if ! docker-compose -f docker-compose.production.yml config > /dev/null 2>&1; then
        error "Invalid docker-compose.production.yml configuration"
        exit 1
    fi
    
    if ! docker-compose -f docker-compose.production.yml -f docker-compose.security.yml config > /dev/null 2>&1; then
        error "Invalid security configuration"
        exit 1
    fi
    
    success "Configuration validation passed"
}

# Main execution
main() {
    log "Starting security setup for Django GraphQL Boilerplate..."
    
    check_root
    check_env_vars
    generate_secrets
    create_directories
    set_permissions
    setup_fail2ban
    setup_monitoring
    create_audit_script
    validate_config
    
    success "Security setup completed successfully!"
    
    echo
    log "Next steps:"
    echo "1. Review and update .env.prod with your specific values"
    echo "2. Update DOMAIN_NAME and SSL_EMAIL in your environment"
    echo "3. Run: docker-compose -f docker-compose.production.yml -f docker-compose.security.yml up -d"
    echo "4. Monitor logs: docker-compose logs -f"
    echo
    warning "Remember to:"
    echo "- Change default passwords"
    echo "- Review firewall settings"
    echo "- Set up regular backups"
    echo "- Monitor security logs"
}

# Run main function
main "$@"
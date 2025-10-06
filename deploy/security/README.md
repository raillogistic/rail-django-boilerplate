# Security Configuration for Django GraphQL Boilerplate

This directory contains security configurations and tools for the production deployment of the Django GraphQL Boilerplate.

## Overview

The security setup includes:

- **Network Segmentation**: Isolated networks for frontend, backend, and monitoring
- **Container Security**: Non-root users, capability dropping, read-only filesystems
- **SSL/TLS**: Automated certificate management with Let's Encrypt
- **Intrusion Prevention**: Fail2ban for blocking malicious IPs
- **Monitoring**: Security event logging and alerting
- **Vulnerability Scanning**: Container image security scanning

## Quick Start

1. **Set Environment Variables**:
   ```bash
   export DOMAIN_NAME="your-domain.com"
   export SSL_EMAIL="admin@your-domain.com"
   export POSTGRES_PASSWORD="your-secure-db-password"
   export JWT_SECRET_KEY="your-jwt-secret"
   export SECRET_KEY="your-django-secret"
   ```

2. **Run Security Setup**:
   ```bash
   chmod +x security/security-setup.sh
   ./security/security-setup.sh
   ```

3. **Deploy with Security**:
   ```bash
   docker-compose -f docker-compose.production.yml -f docker-compose.security.yml up -d
   ```

## Security Features

### Network Security

- **Frontend Network**: Public-facing services (nginx)
- **Backend Network**: Internal services (web, db, redis) - no external access
- **Monitoring Network**: Monitoring services (prometheus, grafana) - no external access

### Container Security

All containers run with:
- Non-root users
- Dropped capabilities (`CAP_DROP: ALL`)
- No new privileges (`no-new-privileges:true`)
- Resource limits
- Read-only root filesystems where possible

### SSL/TLS Configuration

- Automated certificate provisioning with Let's Encrypt
- HTTPS redirect enforcement
- Security headers (HSTS, CSP, etc.)
- Strong cipher suites

### Authentication & Authorization

- Multi-Factor Authentication (MFA) support
- JWT token-based authentication
- Account lockout protection
- Password complexity requirements
- Session timeout controls

### Rate Limiting & DDoS Protection

- GraphQL query complexity analysis
- Rate limiting per IP and user
- Request size limits
- Connection throttling

### Monitoring & Alerting

- Security event logging
- Failed authentication monitoring
- Suspicious activity detection
- Log aggregation and analysis

## Configuration Files

### Environment Variables (.env.prod)

Key security-related environment variables:

```bash
# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key
JWT_ACCESS_TOKEN_LIFETIME=15
JWT_REFRESH_TOKEN_LIFETIME=7

# GraphQL Security
GRAPHQL_DEBUG=False
GRAPHQL_INTROSPECTION=False
GRAPHQL_MAX_QUERY_DEPTH=10

# MFA Settings
MFA_ENABLED=True
MFA_ISSUER_NAME=Django GraphQL Boilerplate

# Account Security
ACCOUNT_LOCKOUT_ENABLED=True
ACCOUNT_LOCKOUT_ATTEMPTS=5
ACCOUNT_LOCKOUT_DURATION=1800

# Security Headers
SECURITY_HSTS_SECONDS=31536000
SECURITY_SSL_REDIRECT=True
```

### Docker Compose Security Override

The `docker-compose.security.yml` file adds:

- Security scanning services
- Intrusion prevention (Fail2ban)
- SSL certificate management
- Security monitoring and logging

## Security Services

### Fail2ban

Monitors logs and bans IPs with suspicious activity:

- SSH brute force protection
- HTTP authentication failures
- Nginx rate limit violations
- Bot detection and blocking

Configuration: `fail2ban/jail.local`

### SSL Certificate Management

Automated SSL certificate provisioning and renewal:

```bash
# Initial certificate setup
docker-compose -f docker-compose.production.yml -f docker-compose.security.yml \
  run --rm certbot

# Certificate renewal (add to cron)
docker-compose -f docker-compose.production.yml -f docker-compose.security.yml \
  run --rm ssl-renew
```

### Security Scanning

Container vulnerability scanning with Trivy:

```bash
# Run security scan
docker-compose -f docker-compose.production.yml -f docker-compose.security.yml \
  --profile security-scan run --rm security-scanner
```

### Audit Logging

Security event monitoring and logging:

- Authentication events
- Authorization failures
- Suspicious network activity
- Configuration changes

Logs are stored in `logs/audit/` and can be forwarded to external SIEM systems.

## Maintenance

### Regular Tasks

1. **Certificate Renewal** (automated via cron):
   ```bash
   0 2 * * * cd /path/to/deploy && docker-compose -f docker-compose.production.yml -f docker-compose.security.yml run --rm ssl-renew
   ```

2. **Security Scanning** (weekly):
   ```bash
   docker-compose --profile security-scan run --rm security-scanner
   ```

3. **Log Rotation**:
   ```bash
   # Add to logrotate.d
   /path/to/deploy/logs/audit/*.log {
       daily
       rotate 30
       compress
       delaycompress
       missingok
       notifempty
   }
   ```

### Monitoring

Monitor security metrics:

- Failed authentication attempts
- Blocked IPs (Fail2ban)
- SSL certificate expiry
- Container vulnerabilities
- Resource usage anomalies

### Backup Security

Ensure backups are:
- Encrypted at rest
- Stored in secure locations
- Regularly tested for restoration
- Access-controlled

## Troubleshooting

### Common Issues

1. **SSL Certificate Issues**:
   ```bash
   # Check certificate status
   docker-compose exec nginx openssl x509 -in /etc/nginx/ssl/cert.pem -text -noout
   
   # Renew certificate manually
   docker-compose run --rm certbot renew --force-renewal
   ```

2. **Fail2ban Not Working**:
   ```bash
   # Check fail2ban status
   docker-compose exec fail2ban fail2ban-client status
   
   # Unban IP
   docker-compose exec fail2ban fail2ban-client set sshd unbanip IP_ADDRESS
   ```

3. **Container Security Issues**:
   ```bash
   # Check container security
   docker-compose exec web id
   docker-compose exec web capsh --print
   ```

### Security Incident Response

1. **Immediate Actions**:
   - Block suspicious IPs
   - Review access logs
   - Check for unauthorized changes
   - Isolate affected services

2. **Investigation**:
   - Analyze audit logs
   - Check container integrity
   - Review authentication events
   - Examine network traffic

3. **Recovery**:
   - Restore from clean backups
   - Update security configurations
   - Patch vulnerabilities
   - Update monitoring rules

## Security Best Practices

1. **Regular Updates**:
   - Keep base images updated
   - Apply security patches promptly
   - Update dependencies regularly

2. **Access Control**:
   - Use strong passwords
   - Enable MFA for all accounts
   - Implement least privilege principle
   - Regular access reviews

3. **Monitoring**:
   - Monitor all security events
   - Set up alerting for anomalies
   - Regular security assessments
   - Penetration testing

4. **Backup & Recovery**:
   - Regular encrypted backups
   - Test restoration procedures
   - Offsite backup storage
   - Disaster recovery planning

## Compliance

This security configuration helps meet requirements for:

- GDPR (data protection)
- SOC 2 (security controls)
- ISO 27001 (information security)
- PCI DSS (payment security)

## Support

For security issues or questions:

1. Check the troubleshooting section
2. Review security logs
3. Consult the Django GraphQL Boilerplate documentation
4. Contact the security team

## Security Contacts

- **Security Team**: security@your-domain.com
- **Incident Response**: incident@your-domain.com
- **Emergency**: +1-XXX-XXX-XXXX
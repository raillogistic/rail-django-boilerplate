# SSL Certificate Setup for Windows

For Windows deployment, consider using one of these options:

1. **win-acme (Recommended for Let's Encrypt)**
   - Download from: https://www.win-acme.com/
   - Example command: wacs.exe --target manual --host localhost --emailaddress admin@localhost

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
